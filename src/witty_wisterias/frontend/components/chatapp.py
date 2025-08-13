import reflex as rx

from frontend.components.chat_bubble import chat_bubble_component
from frontend.components.image_button import send_image_component
from frontend.components.text_button import send_text_component
from frontend.states.chat_state import ChatState


def chat_app() -> rx.Component:
    """Main chat application component."""
    return rx.vstack(
        rx.auto_scroll(
            rx.foreach(
                ChatState.messages,
                lambda message: chat_bubble_component(
                    message["message"],
                    # Use UserID as fallback for Username
                    rx.cond(message["user_name"], message["user_name"], message["user_id"]),
                    message["user_profile_image"],
                    message["own_message"],
                    message["is_image_message"],
                ),
            ),
            class_name="flex flex-col gap-4 pb-6 pt-6 h-full w-full mt-5 bg-gray-50 p-5 rounded-xl shadow-sm",
        ),
        rx.divider(),
        rx.hstack(
            send_text_component(),
            send_image_component(),
            class_name="mt-auto mb-3 w-full",
        ),
        spacing="4",
        class_name="h-screen w-full mx-5",
    )
