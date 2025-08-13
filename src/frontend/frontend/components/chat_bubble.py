import reflex as rx
from PIL import Image


def chat_bubble_component(
    message: str | Image.Image,
    user_name: str,
    user_profile_image: str | None = None,
    own_message: bool = False,
    is_image_message: bool = False,
) -> rx.Component:
    """Creates a chat bubble component for displaying messages in the chat application.

    Args:
        message (str): The content of the message, either text or base64-encoded image.
        user_name (str): The name of the user who sent the message.
        user_profile_image (str): The URL of the user's profile image.
        own_message (bool): Whether the message is sent by the current user.
        is_image_message (bool): Whether the message is an image. If True, `message` should be a Pillow Image.

    Returns:
        rx.Component: A component representing the chat bubble.
    """
    avatar = rx.avatar(
        src=user_profile_image,
        fallback=user_name[:2],
        radius="large",
        size="3",
    )
    message_content = rx.vstack(
        rx.text(user_name, class_name="font-semibold"),
        rx.cond(
            is_image_message,
            rx.image(src=message, alt="Image message", max_width="500px", max_height="500px"),
            rx.text(message, class_name="text-gray-800"),
        ),
        class_name="rounded-lg",
        spacing="0",
    )

    return rx.hstack(
        rx.cond(
            own_message,
            [
                message_content,
                avatar,
            ],
            [
                avatar,
                message_content,
            ],
        ),
        class_name="items-start space-x-2 bg-gray-100 p-4 rounded-lg shadow-sm",
        style={"alignSelf": rx.cond(own_message, "flex-end", "flex-start")},
    )
