import reflex as rx

from frontend.components.image_button import send_image_component
from frontend.components.text_button import send_text_component


def chat_app() -> rx.Component:
    """Main chat application component."""
    return rx.vstack(
        rx.box(
            "This is our chat app! (TEMP)",
            class_name="h-full w-full mt-5 bg-gray-50 p-5 rounded-xl shadow-sm",
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
