import asyncio
import io
import random
from typing import TypedDict

import reflex as rx
import requests
from PIL import Image


class Message(TypedDict):
    """A message in the chat application."""

    message: str | Image.Image
    user_id: str
    user_name: str
    user_profile_image: str | None
    own_message: bool
    is_image_message: bool


class ChatState(rx.State):
    """The Chat app state, used to handle Messages."""

    messages: list[Message] = rx.field(default_factory=list)

    @rx.event
    def send_text(self, form_data: dict[str, str]) -> None:
        """
        Reflex Event when a text message is sent.

        Args:
            form_data (dict[str, str]): The form data containing the message in the `message` field.
        """
        message = form_data.get("message", "").strip()
        if message:
            self.messages.append(
                Message(
                    message=message,
                    user_id="ME",
                    user_name="User Name",
                    user_profile_image=None,
                    own_message=True,
                    is_image_message=False,
                )
            )

    @rx.event
    def send_image(self, form_data: dict[str, str]) -> None:
        """
        Reflex Event when an image message is sent.

        Args:
            form_data (dict[str, str]): The form data containing the image URL in the `message` field.
        """
        message = form_data.get("message", "").strip()
        if message:
            response = requests.get(message, timeout=10)
            img = Image.open(io.BytesIO(response.content))
            self.messages.append(
                Message(
                    message=img,
                    user_id="ME",
                    user_name="User Name",
                    user_profile_image=None,
                    own_message=True,
                    is_image_message=True,
                )
            )

    @rx.event(background=True)
    async def check_messages(self) -> None:
        """Reflex Background Check for new messages."""
        while True:
            # Simulate checking for new messages
            await asyncio.sleep(random.randint(5, 10))
            async with self:
                self.messages.append(
                    Message(
                        message="New message from background task",
                        user_id="BOT",
                        user_name="Bot",
                        user_profile_image=None,
                        own_message=False,
                        is_image_message=False,
                    )
                )
