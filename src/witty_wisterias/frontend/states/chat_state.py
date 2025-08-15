import asyncio
import base64
import io
import json
import threading
from collections.abc import AsyncGenerator, Generator
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal, TypedDict, cast

import reflex as rx
import requests
from backend.backend import Backend
from backend.cryptographer import Cryptographer
from backend.message_format import EventType, MessageFormat
from PIL import Image

from frontend.states.progress_state import ProgressState


class MessageJson(TypedDict):
    """
    Defines the structure of the JSON representation of a message.
    This is used for serialization and deserialization of messages.
    """

    message: str
    user_id: str
    receiver_id: str | None
    user_name: str
    user_profile_image: str | None
    own_message: bool
    is_image_message: bool
    timestamp: float


@dataclass
class Message:
    """A message in the chat application."""

    message: str | Image.Image
    user_id: str
    receiver_id: str | None
    user_name: str
    user_profile_image: str | None
    own_message: bool
    is_image_message: bool
    timestamp: float

    @staticmethod
    def from_message_format(message_format: MessageFormat) -> "Message":
        """
        Convert a MessageFormat object to a Message object.

        Args:
            message_format (MessageFormat): The MessageFormat object to convert.

        Returns:
            Message: A Message object created from the MessageFormat.
        """
        return Message(
            message=message_format.content,
            user_id=message_format.sender_id,
            receiver_id=message_format.receiver_id if message_format.receiver_id != "None" else None,
            user_name=message_format.extra_event_info.user_name or message_format.sender_id,
            user_profile_image=message_format.extra_event_info.user_image,
            own_message=str(ChatState.user_id) == message_format.sender_id,
            is_image_message=message_format.event_type in (EventType.PUBLIC_IMAGE, EventType.PRIVATE_IMAGE),
            timestamp=message_format.timestamp,
        )

    @staticmethod
    def from_dict(data: MessageJson) -> "Message":
        """
        Convert a dictionary to a Message object.

        Args:
            data (dict[str, str]): The dictionary containing message data.

        Returns:
            Message: A Message object created from the dictionary.
        """
        if data.get("is_image_message", False):
            # Decode the base64 image data to an Image object
            image_data = base64.b64decode(data["message"])
            message_content = Image.open(io.BytesIO(image_data))
            message_content = message_content.convert("RGB")
        else:
            message_content = data["message"]
        return Message(
            message=message_content,
            user_id=data["user_id"],
            receiver_id=data.get("receiver_id"),
            user_name=data["user_name"],
            user_profile_image=data.get("user_profile_image"),
            own_message=data.get("own_message", False),
            is_image_message=data.get("is_image_message", False),
            timestamp=float(data["timestamp"]),
        )

    def to_dict(self) -> MessageJson:
        """
        Convert the message into a Python dictionary.

        Returns:
            MessageJson: A dictionary representation of the message.
        """
        if isinstance(self.message, Image.Image):
            # Convert the image to bytes and encode it in base64 (JPEG to save limited LocalStorage space)
            buffered = io.BytesIO()
            self.message.save(buffered, format="JPEG")
            message_data = base64.b64encode(buffered.getvalue()).decode("utf-8")
        else:
            message_data = self.message

        return {
            "message": message_data,
            "user_id": self.user_id,
            "receiver_id": self.receiver_id,
            "user_name": self.user_name,
            "user_profile_image": self.user_profile_image,
            "own_message": self.own_message,
            "is_image_message": self.is_image_message,
            "timestamp": self.timestamp,
        }


class ChatState(rx.State):
    """The Chat app state, used to handle Messages."""

    # Tos Accepted (Note: We need to use a string here because LocalStorage does not support booleans)
    tos_accepted: str = rx.LocalStorage("False", name="tos_accepted", sync=True)
    # List of Messages
    messages: list[Message] = rx.field(default_factory=list)
    # We need to store our own private messages in LocalStorage, as we cannot decrypt them from the Database
    own_private_messages: str = rx.LocalStorage("[]", name="private_messages", sync=True)
    # Chat Partners
    chat_partners: list[str] = rx.field(default_factory=list)
    # Current Selected Chat
    selected_chat: str = rx.LocalStorage("Public", name="selected_chat", sync=True)

    # Own User Data
    user_id: str = rx.LocalStorage("", name="user_id", sync=True)
    user_name: str = rx.LocalStorage("", name="user_name", sync=True)
    user_profile_image: str | None = rx.LocalStorage(None, name="user_profile_image", sync=True)
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
        current_keys = self.get_key_storage(storage_name)
        current_keys[user_id] = verify_key
        self.dump_key_storage(storage_name, current_keys)

    def register_chat_partner(self, user_id: str) -> None:
        """
        Register a new chat partner by adding their user ID to the chat partners list.

        Args:
            user_id (str): The user ID of the chat partner to register.
        """
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
    def edit_user_info(self, form_data: dict[str, str]) -> Generator[None, None]:
        """
        Reflex Event when the user information is edited.

        Args:
            form_data (dict[str, str]): The form data containing the user information.
        """
        self.user_name = form_data.get("user_name", "").strip()
        self.user_profile_image = form_data.get("user_profile_image", "").strip() or None
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
    def send_public_text(self, form_data: dict[str, str]) -> Generator[None, None]:
        """
        Reflex Event when a text message is sent.

        Args:
            form_data (dict[str, str]): The form data containing the message in the `message` field.
        """
        message = form_data.get("message", "").strip()
        if message:
            # Sending Placebo Progress Bar
            yield ProgressState.public_message_progress

            message_timestamp = datetime.now(UTC).timestamp()
            # Appending new own message
            self.messages.append(
                Message(
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

            # Posting message to backend
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
    def send_public_image(self, form_data: dict[str, str]) -> Generator[None, None]:
        """
        Reflex Event when an image message is sent.

        Args:
            form_data (dict[str, str]): The form data containing the image URL in the `message` field.
        """
        message = form_data.get("message", "").strip()
        if message:
            # Temporary
            response = requests.get(message, timeout=10)
            img = Image.open(io.BytesIO(response.content))

            # Sending Placebo Progress Bar
            yield ProgressState.public_message_progress

            message_timestamp = datetime.now(UTC).timestamp()
            # Appending new own message
            self.messages.append(
                Message(
                    message=img,
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

            # Posting message to backend
            message_format = MessageFormat(
                sender_id=self.user_id,
                event_type=EventType.PUBLIC_IMAGE,
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
    def send_private_text(self, form_data: dict[str, str]) -> Generator[None, None]:
        """
        Reflex Event when a private text message is sent.

        Args:
            form_data (dict[str, str]): The form data containing the message in the `message` field.
        """
        message = form_data.get("message", "").strip()
        receiver_id = form_data.get("receiver_id", "").strip() or self.selected_chat
        if message and receiver_id:
            if receiver_id not in self.get_key_storage("public_keys"):
                # Cant message someone who is not registered
                raise ValueError("Recipients Public Key is not registered.")

            self.register_chat_partner(receiver_id)
            self.selected_chat = receiver_id
            yield

            # Sending Placebo Progress Bar
            yield ProgressState.private_message_progress

            message_timestamp = datetime.now(UTC).timestamp()
            # Appending new own message
            chat_message = Message(
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
            # Also append to own private messages, as we cannot decrypt them from the Database
            own_private_messages_json = json.loads(self.own_private_messages)
            own_private_messages_json.append(chat_message.to_dict())
            # Encode back to String JSON
            self.own_private_messages = json.dumps(own_private_messages_json)
            yield

            # Posting message to backend
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
    def send_private_image(self, form_data: dict[str, str]) -> Generator[None, None]:
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

            self.register_chat_partner(receiver_id)
            self.selected_chat = receiver_id
            yield

            # Temporary
            response = requests.get(message, timeout=10)
            img = Image.open(io.BytesIO(response.content))

            # Sending Placebo Progress Bar
            yield ProgressState.private_message_progress

            message_timestamp = datetime.now(UTC).timestamp()
            # Appending new own message
            chat_message = Message(
                message=img,
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

            # Posting message to backend
            message_format = MessageFormat(
                sender_id=self.user_id,
                receiver_id=receiver_id,
                event_type=EventType.PRIVATE_IMAGE,
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

    @rx.event(background=True)
    async def check_messages(self) -> None:
        """Reflex Background Check for new messages."""
        while True:
            async with self:
                # Read Verify and Public Keys from Backend
                verify_keys, public_keys = Backend.read_public_keys()
                for user_id, verify_key in verify_keys.items():
                    self.add_key_storage("verify_keys", user_id, verify_key)
                for user_id, public_key in public_keys.items():
                    self.add_key_storage("public_keys", user_id, public_key)

                # Public Chat Messages
                for message in Backend.read_public_messages():
                    # Check if the message is already in the chat using timestamp
                    message_exists = any(
                        msg.timestamp == message.timestamp and msg.user_id == message.sender_id
                        for msg in self.messages
                    )

                    # Check if message is not already in the chat
                    if not message_exists:
                        self.messages.append(
                            Message(
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
                # Private Chat Messages
                backend_private_message_formats = Backend.read_private_messages(self.user_id, self.private_key)
                backend_private_messages = [
                    Message.from_message_format(message_format) for message_format in backend_private_message_formats
                ]
                own_private_messages_json = json.loads(self.own_private_messages)
                own_private_messages = [Message.from_dict(message_data) for message_data in own_private_messages_json]
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
        """Reflex Event that is called when the app starts up."""
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
