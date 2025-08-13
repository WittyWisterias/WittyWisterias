import asyncio
import io
import json
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Literal, TypedDict, cast

import reflex as rx
import requests
from backend.backend import Backend
from backend.cryptographer import Cryptographer
from backend.message_format import EventType, MessageFormat
from PIL import Image


class Message(TypedDict):
    """A message in the chat application."""

    message: str | Image.Image
    user_id: str
    user_name: str
    user_profile_image: str | None
    own_message: bool
    is_image_message: bool
    timestamp: float


class ChatState(rx.State):
    """The Chat app state, used to handle Messages."""

    # List of Messages
    messages: list[Message] = rx.field(default_factory=list)
    # Own User Data
    user_id: str = rx.LocalStorage("", name="user_id", sync=True)
    user_name: str = rx.LocalStorage("", name="user_name", sync=True)
    user_profile_image: str | None = rx.LocalStorage(None, name="user_profile_image", sync=True)
    # Own Signing key and Others Verify Keys for Global Chat
    signing_key: str = rx.LocalStorage("", name="signing_key", sync=True)
    verify_keys_storage: str = rx.LocalStorage("{}", name="verify_keys_storage", sync=True)
    # Own Private Keys and Others Public Keys for Private Chats
    private_keys_storage: str = rx.LocalStorage("{}", name="private_keys_storage", sync=True)
    public_keys_storage: str = rx.LocalStorage("{}", name="public_keys_storage", sync=True)

    # Verify Keys Storage Helpers
    def get_key_storage(self, storage_name: Literal["verify_keys", "private_keys", "public_keys"]) -> dict[str, str]:
        """
        Get the key storage for the specified storage name.

        Args:
            storage_name (Literal["verify_keys", "private_keys", "public_keys"]): The name of the storage to retrieve.

        Returns:
            dict[str, str]: A dictionary containing the keys and their corresponding values.
        """
        storage = self.__getattribute__(f"{storage_name}_storage")
        return cast("dict[str, str]", json.loads(storage))

    def dump_key_storage(
        self, storage_name: Literal["verify_keys", "private_keys", "public_keys"], value: dict[str, str]
    ) -> None:
        """
        Dump the key storage to the specified storage name.

        Args:
            storage_name (Literal["verify_keys", "private_keys", "public_keys"]): The name of the storage to dump to.
            value (dict[str, str]): The dictionary containing the userIDs and their Keys.
        """
        self.__setattr__(f"{storage_name}_storage", json.dumps(value))

    def add_key_storage(
        self, storage_name: Literal["verify_keys", "private_keys", "public_keys"], user_id: str, verify_key: str
    ) -> None:
        """
        Add a userID and its corresponding key to the specified storage.

        Args:
            storage_name (Literal["verify_keys", "private_keys", "public_keys"]): The name of the storage to add to.
            user_id (str): The user ID to add.
            verify_key (str): The key to associate with the user ID.
        """
        current_keys = self.get_key_storage(storage_name)
        current_keys[user_id] = verify_key
        self.dump_key_storage(storage_name, current_keys)

    @rx.event
    def send_text(self, form_data: dict[str, str]) -> None:
        """
        Reflex Event when a text message is sent.

        Args:
            form_data (dict[str, str]): The form data containing the message in the `message` field.
        """
        message = form_data.get("message", "").strip()
        if message:
            message_timestamp = datetime.now(UTC).timestamp()
            # Appending new own message
            self.messages.append(
                Message(
                    message=message,
                    user_id=self.user_id,
                    user_name=self.user_name,
                    user_profile_image=self.user_profile_image,
                    own_message=True,
                    is_image_message=False,
                    timestamp=message_timestamp,
                )
            )
            # Posting message to backend
            message_format = MessageFormat(
                sender_id=self.user_id,
                event_type=EventType.PUBLIC_TEXT,
                content=message,
                timestamp=message_timestamp,
                signing_key=self.signing_key,
                verify_key=self.get_key_storage("verify_keys")[self.user_id],
            )
            Backend.send_public_text(message_format)

    @rx.event
    def send_image(self, form_data: dict[str, str]) -> None:
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

            message_timestamp = datetime.now(UTC).timestamp()
            self.messages.append(
                Message(
                    message=img,
                    user_id=self.user_id,
                    user_name=self.user_name,
                    user_profile_image=self.user_profile_image,
                    own_message=True,
                    is_image_message=True,
                    timestamp=message_timestamp,
                )
            )

    @rx.event(background=True)
    async def check_messages(self) -> None:
        """Reflex Background Check for new messages."""
        while True:
            async with self:
                for message in Backend.read_public_text():
                    # Check if the message is already in the chat using timestamp
                    message_exists = any(
                        msg["timestamp"] == message.timestamp and msg["user_id"] == message.sender_id
                        for msg in self.messages
                    )

                    # Check if message is not already in the chat
                    if not message_exists:
                        self.messages.append(
                            Message(
                                message=message.content,
                                user_id=message.sender_id,
                                user_name=message.extra_event_info.user_name,
                                user_profile_image=message.extra_event_info.user_image,
                                own_message=self.user_id == message.sender_id,
                                is_image_message=False,
                                timestamp=message.timestamp,
                            )
                        )

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
