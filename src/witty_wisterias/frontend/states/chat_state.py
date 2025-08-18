import asyncio
import base64
import io
import json
import threading
from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from typing import Any, Literal, cast

import reflex as rx
from backend.backend import Backend
from backend.cryptographer import Cryptographer
from backend.message_format import EventType, MessageFormat, MessageState
from backend.user_input_handler import UserInputHandler
from PIL import Image

from frontend.states.progress_state import ProgressState
from frontend.states.webcam_state import WebcamStateMixin


class ChatState(WebcamStateMixin, rx.State):
    """The Chat app state, used to handle Messages. Main Frontend Entrypoint."""

    # Tos Accepted (Note: We need to use a string here because LocalStorage does not support booleans)
    tos_accepted: str = rx.LocalStorage("False", name="tos_accepted", sync=True)
    # List of Messages
    messages: list[MessageState] = rx.field(default_factory=list)
    # We need to store our own private messages in LocalStorage, as we cannot decrypt them from the Database
    own_private_messages: str = rx.LocalStorage("[]", name="private_messages", sync=True)
    # Chat Partners
    chat_partners: list[str] = rx.field(default_factory=list)
    # Current Selected Chat
    selected_chat: str = rx.LocalStorage("Public", name="selected_chat", sync=True)

    # Own User Data
    user_id: str = rx.LocalStorage("", name="user_id", sync=True)
    user_name: str = rx.LocalStorage("", name="user_name", sync=True)
    user_profile_image: str = rx.LocalStorage("", name="user_profile_image", sync=True)
    # Own Signing key and Others Verify Keys for Global Chat
    signing_key: str = rx.LocalStorage("", name="signing_key", sync=True)
    verify_keys_storage: str = rx.LocalStorage("{}", name="verify_keys_storage", sync=True)
    # Own Private Keys and Others Public Keys for Private Chats
    private_key: str = rx.LocalStorage("", name="private_key", sync=True)
    public_keys_storage: str = rx.LocalStorage("{}", name="public_keys_storage", sync=True)

    # Verify Keys Storage Helpers
    def get_key_storage(self, storage_name: Literal["verify_keys", "public_keys"]) -> dict[str, str]:
        """
        Get the key storage for the specified storage name.

        Args:
            storage_name (Literal["verify_keys", "public_keys"]): The name of the storage to retrieve.

        Returns:
            dict[str, str]: A dictionary containing the keys and their corresponding values.
        """
        storage = self.__getattribute__(f"{storage_name}_storage")
        # Note: Casting Type as json.loads returns typing.Any
        return cast("dict[str, str]", json.loads(storage))

    def dump_key_storage(self, storage_name: Literal["verify_keys", "public_keys"], value: dict[str, str]) -> None:
        """
        Dump the key storage to the specified storage name.

        Args:
            storage_name (Literal["verify_keys", "public_keys"]): The name of the storage to dump to.
            value (dict[str, str]): The dictionary containing the userIDs and their Keys.
        """
        self.__setattr__(f"{storage_name}_storage", json.dumps(value))

    def add_key_storage(
        self, storage_name: Literal["verify_keys", "public_keys"], user_id: str, verify_key: str
    ) -> None:
        """
        Add a userID and its corresponding key to the specified storage.

        Args:
            storage_name (Literal["verify_keys", "public_keys"]): The name of the storage to add to.
            user_id (str): The user ID to add.
            verify_key (str): The key to associate with the user ID.
        """
        # Loading the Key Storage into a dict
        current_keys = self.get_key_storage(storage_name)
        # Adding the Key
        current_keys[user_id] = verify_key
        # Dumping the new Key Storage
        self.dump_key_storage(storage_name, current_keys)

    # Registering Private Chat Partners to show them in the Private Chats list
    def register_chat_partner(self, user_id: str) -> None:
        """
        Register a new chat partner by adding their user ID to the chat partners list.

        Args:
            user_id (str): The user ID of the chat partner to register.
        """
        # Avoid Duplicates
        if user_id not in self.chat_partners:
            self.chat_partners.append(user_id)
            # Sort to find the chat partner in the list more easily
            self.chat_partners.sort()

    @rx.event
    def accept_tos(self) -> Generator[None, None]:
        """Reflex Event when the Terms of Service are accepted."""
        self.tos_accepted = "True"
        yield

    @rx.event
    def edit_user_info(self, form_data: dict[str, Any]) -> Generator[None, None]:
        """
        Reflex Event when the user information is edited.

        Args:
            form_data (dict[str, str]): The form data containing the user information.
        """
        self.user_name = form_data.get("user_name", "").strip()
        # A User Profile Image is not required in the Form.
        self.user_profile_image = form_data.get("user_profile_image", "").strip()
        yield

    @rx.event
    def select_chat(self, chat_name: str) -> Generator[None, None]:
        """
        Reflex Event when a chat is selected.

        Args:
            chat_name (str): The name of the chat to select.
        """
        self.selected_chat = chat_name
        yield

    @rx.event
    def start_webcam(self, _: dict[str, str]) -> None:
        """
        Start the webcam capture loop.

        Args:
            _ (dict[str, str]): The form data containing the message in the `message` field. Unused.
        """
        self.recording = True
        yield ChatState.capture_loop

    @rx.event
    async def send_public_text(self, _: dict[str, Any]) -> Generator[None, None]:
        """
        Reflex Event when a text message is sent.

        Args:
            _ (dict[str, str]): The form data containing the message in the `message` field. Unused.
        """
        # Stop Webcam Stream
        ChatState.disable_webcam()
        # Converting last Webcam Frame to Text
        message = UserInputHandler.image_to_text(str(self.frame_data))

        if message:
            # Sending Placebo Progress Bar
            yield ProgressState.public_message_progress

            message_timestamp = datetime.now(UTC).timestamp()
            # Appending new own message to show in the Chat
            self.messages.append(
                MessageState(
                    message=message,
                    user_id=self.user_id,
                    user_name=self.user_name,
                    receiver_id=None,
                    user_profile_image=self.user_profile_image,
                    own_message=True,
                    is_image_message=False,
                    timestamp=message_timestamp,
                )
            )
            yield

            # Formatting the message for the Backend
            message_format = MessageFormat(
                sender_id=self.user_id,
                event_type=EventType.PUBLIC_TEXT,
                content=message,
                timestamp=message_timestamp,
                signing_key=self.signing_key,
                verify_key=self.get_key_storage("verify_keys")[self.user_id],
                sender_username=self.user_name,
                sender_profile_image=self.user_profile_image,
            )
            # Note: We need to use threading here, even if it looks odd. This is because the
            # Backend.send_public_message method blocks the UI thread. So we need to run it in a separate thread.
            # Something like asyncio.to_thread or similar doesn't work here, not 100% sure why, my best guess is
            # that it does not separate from the UI thread properly. So threading is the next best option.
            # If you find something better, please update this.
            threading.Thread(target=Backend.send_public_message, args=(message_format,), daemon=True).start()

    @rx.event
    def send_public_image(self, form_data: dict[str, Any]) -> Generator[None, None]:
        """
        Reflex Event when an image message is sent.

        Args:
            form_data (dict[str, str]): The form data containing the image URL in the `message` field.
        """
        message = form_data.get("message", "").strip()
        if message:
            # Converting the Image Description to an Image
            base64_image = UserInputHandler.text_to_image(message)
            # Decode the Base64 string to bytes
            image_data = base64.b64decode(base64_image)
            # Open the image stream with PIL
            pil_image = Image.open(io.BytesIO(image_data))

            # Sending Placebo Progress Bar
            yield ProgressState.public_message_progress

            message_timestamp = datetime.now(UTC).timestamp()
            # Appending new own message to show in the Chat
            self.messages.append(
                MessageState(
                    message=pil_image,
                    user_id=self.user_id,
                    user_name=self.user_name,
                    receiver_id=None,
                    user_profile_image=self.user_profile_image,
                    own_message=True,
                    is_image_message=True,
                    timestamp=message_timestamp,
                )
            )
            yield

            # Formatting the message for the Backend
            message_format = MessageFormat(
                sender_id=self.user_id,
                event_type=EventType.PUBLIC_IMAGE,
                content=base64_image,
                timestamp=message_timestamp,
                signing_key=self.signing_key,
                verify_key=self.get_key_storage("verify_keys")[self.user_id],
                sender_username=self.user_name,
                sender_profile_image=self.user_profile_image,
            )
            # Note: We need to use threading here, even if it looks odd. This is because the
            # Backend.send_public_message method blocks the UI thread. So we need to run it in a separate thread.
            # Something like asyncio.to_thread or similar doesn't work here, not 100% sure why, my best guess is
            # that it does not separate from the UI thread properly. So threading is the next best option.
            # If you find something better, please update this.
            threading.Thread(target=Backend.send_public_message, args=(message_format,), daemon=True).start()

    @rx.event
    def send_private_text(self, form_data: dict[str, Any]) -> Generator[None, None]:
        """
        Reflex Event when a private text message is sent.

        Args:
            form_data (dict[str, str]): The form data containing the message in the `message` field.
        """
        # Stop Webcam Stream
        ChatState.disable_webcam()
        # Converting last Webcam Frame to Text
        message = UserInputHandler.image_to_text(str(self.frame_data))

        receiver_id = form_data.get("receiver_id", "").strip() or self.selected_chat
        if message and receiver_id:
            if receiver_id not in self.get_key_storage("public_keys"):
                # Cant message someone who is not registered
                raise ValueError("Recipients Public Key is not registered.")

            # Register Chat Partner and select the Chat
            self.register_chat_partner(receiver_id)
            self.selected_chat = receiver_id
            yield

            # Sending Placebo Progress Bar
            yield ProgressState.private_message_progress

            message_timestamp = datetime.now(UTC).timestamp()
            # Appending new own message to show in the Chat
            chat_message = MessageState(
                message=message,
                user_id=self.user_id,
                user_name=self.user_name,
                receiver_id=receiver_id,
                user_profile_image=self.user_profile_image,
                own_message=True,
                is_image_message=False,
                timestamp=message_timestamp,
            )

            self.messages.append(chat_message)
            # Also append to own private messages LocalStorage, as we cannot decrypt them from the Database
            own_private_messages_json = json.loads(self.own_private_messages)
            own_private_messages_json.append(chat_message.to_dict())
            # Encode back to String JSON
            self.own_private_messages = json.dumps(own_private_messages_json)
            yield

            # Formatting the message for the Backend
            message_format = MessageFormat(
                sender_id=self.user_id,
                receiver_id=receiver_id,
                event_type=EventType.PRIVATE_TEXT,
                content=message,
                timestamp=message_timestamp,
                own_public_key=self.get_key_storage("public_keys")[self.user_id],
                receiver_public_key=self.get_key_storage("public_keys")[receiver_id],
                private_key=self.private_key,
                sender_username=self.user_name,
                sender_profile_image=self.user_profile_image,
            )
            # Note: We need to use threading here, even if it looks odd. This is because the
            # Backend.send_private_message method blocks the UI thread. So we need to run it in a separate thread.
            # Something like asyncio.to_thread or similar doesn't work here, not 100% sure why, my best guess is
            # that it does not separate from the UI thread properly. So threading is the next best option.
            # If you find something better, please update this.
            threading.Thread(target=Backend.send_private_message, args=(message_format,), daemon=True).start()

    @rx.event
    def send_private_image(self, form_data: dict[str, Any]) -> Generator[None, None]:
        """
        Reflex Event when a private image message is sent.

        Args:
            form_data (dict[str, str]): The form data containing the image URL in the `message` field.
        """
        message = form_data.get("message", "").strip()
        receiver_id = form_data.get("receiver_id", "").strip() or self.selected_chat
        if message and receiver_id:
            if receiver_id not in self.get_key_storage("public_keys"):
                # Cant message someone who is not registered
                raise ValueError("Recipients Public Key is not registered.")

            # Register Chat Partner and select the Chat
            self.register_chat_partner(receiver_id)
            self.selected_chat = receiver_id
            yield

            # Converting the Image Description to an Image
            base64_image = UserInputHandler.text_to_image(message)
            # Decode the Base64 string to bytes
            image_data = base64.b64decode(base64_image)
            # Open the image stream with PIL
            pil_image = Image.open(io.BytesIO(image_data))

            # Sending Placebo Progress Bar
            yield ProgressState.private_message_progress

            message_timestamp = datetime.now(UTC).timestamp()
            # Appending new own message to show in the Chat
            chat_message = MessageState(
                message=pil_image,
                user_id=self.user_id,
                user_name=self.user_name,
                receiver_id=receiver_id,
                user_profile_image=self.user_profile_image,
                own_message=True,
                is_image_message=True,
                timestamp=message_timestamp,
            )
            self.messages.append(chat_message)
            # Also append to own private messages, as we cannot decrypt them from the Database
            own_private_messages_json = json.loads(self.own_private_messages)
            own_private_messages_json.append(chat_message.to_dict())
            # Encode back to String JSON
            self.own_private_messages = json.dumps(own_private_messages_json)
            yield

            # Formatting the message for the Backend
            message_format = MessageFormat(
                sender_id=self.user_id,
                receiver_id=receiver_id,
                event_type=EventType.PRIVATE_IMAGE,
                content=base64_image,
                timestamp=message_timestamp,
                own_public_key=self.get_key_storage("public_keys")[self.user_id],
                receiver_public_key=self.get_key_storage("public_keys")[receiver_id],
                private_key=self.private_key,
                sender_username=self.user_name,
                sender_profile_image=self.user_profile_image,
            )
            # Note: We need to use threading here, even if it looks odd. This is because the
            # Backend.send_private_message method blocks the UI thread. So we need to run it in a separate thread.
            # Something like asyncio.to_thread or similar doesn't work here, not 100% sure why, my best guess is
            # that it does not separate from the UI thread properly. So threading is the next best option.
            # If you find something better, please update this.
            threading.Thread(target=Backend.send_private_message, args=(message_format,), daemon=True).start()

    @rx.event(background=True)
    async def check_messages(self) -> None:
        """Reflex Background Check for new messages."""
        while True:
            # To not block the UI thread, we run this in an executor before the async with self.
            loop = asyncio.get_running_loop()
            verify_keys, public_keys = await loop.run_in_executor(None, Backend.read_public_keys)
            public_messages = await loop.run_in_executor(None, Backend.read_public_messages)
            backend_private_message_formats = await loop.run_in_executor(
                None, Backend.read_private_messages, self.user_id, self.private_key
            )
            async with self:
                # Push Verify and Public Keys to the LocalStorage
                for user_id, verify_key in verify_keys.items():
                    self.add_key_storage("verify_keys", user_id, verify_key)
                for user_id, public_key in public_keys.items():
                    self.add_key_storage("public_keys", user_id, public_key)

                # Public Chat Messages
                for message in public_messages:
                    # Check if the message is already in the chat using timestamp
                    message_exists = any(
                        all_messages.timestamp == message.timestamp and all_messages.user_id == message.sender_id
                        for all_messages in self.messages
                    )

                    # Check if message is not already in the chat
                    if not message_exists:
                        # Convert the Backend Format to the Frontend Format (MessageState)
                        self.messages.append(
                            MessageState(
                                message=message.content,
                                user_id=message.sender_id,
                                user_name=message.extra_event_info.user_name,
                                receiver_id=None,
                                user_profile_image=message.extra_event_info.user_image,
                                own_message=self.user_id == message.sender_id,
                                is_image_message=message.event_type == EventType.PUBLIC_IMAGE,
                                timestamp=message.timestamp,
                            )
                        )

                # Private Chat Messages stored in the Backend
                backend_private_messages = [
                    MessageState.from_message_format(message_format, str(self.user_id))
                    for message_format in backend_private_message_formats
                ]
                # Our own Private Messages, stored in the LocalStorage as we cannot self-decrypt them from the Backend
                own_private_messages_json = json.loads(self.own_private_messages)
                own_private_messages = [
                    MessageState.from_dict(message_data) for message_data in own_private_messages_json
                ]
                # Sort them based on their timestamp
                sorted_private_messages = sorted(
                    backend_private_messages + own_private_messages,
                    key=lambda msg: msg.timestamp,
                )
                for message in sorted_private_messages:
                    # Add received chat partner to chat partners list
                    if message.user_id != self.user_id:
                        self.register_chat_partner(message.user_id)
                    # Check if the message is already in the chat using timestamp
                    message_exists = any(
                        msg.timestamp == message.timestamp and msg.user_id == message.user_id for msg in self.messages
                    )

                    # Check if message is not already in the chat
                    if not message_exists:
                        self.messages.append(message)

            # Wait for 5 seconds before checking for new messages again to avoid excessive load
            await asyncio.sleep(5)

    @rx.event
    async def startup_event(self) -> AsyncGenerator[None, None]:
        """Reflex Event that is called when the app starts up. Main Entrypoint for the Frontend and spawns Backend."""
        # Start Message Checking Background Task
        yield ChatState.check_messages

        # Initialize user_id if not already set
        if not self.user_id:
            # Simulate fetching a user ID from an external source
            self.user_id = Cryptographer.generate_random_user_id()

        # Generate new Signing Key Pair if not set
        if not self.signing_key or self.user_id not in self.get_key_storage("verify_keys"):
            self.signing_key, verify_key = Cryptographer.generate_signing_key_pair()
            self.add_key_storage("verify_keys", self.user_id, verify_key)

        # Generate new Private Key Pair if not set
        if not self.private_key or self.user_id not in self.get_key_storage("public_keys"):
            self.private_key, public_key = Cryptographer.generate_encryption_key_pair()
            self.add_key_storage("public_keys", self.user_id, public_key)

        # Ensure the Public Keys are Uploaded
        verify_key = self.get_key_storage("verify_keys")[self.user_id]
        public_key = self.get_key_storage("public_keys")[self.user_id]
        Backend.push_public_keys(self.user_id, verify_key, public_key)
