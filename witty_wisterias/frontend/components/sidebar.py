import reflex as rx

from frontend.components.create_chat import create_chat_component
from frontend.components.user_info import user_info_component
from frontend.states.chat_state import ChatState
from frontend.states.progress_state import ProgressState


def chat_sidebar() -> rx.Component:
    """
    Sidebar component for the chat application, which allows users to select the public Chat, different private
    Chats and to view and edit their own User Information.

    Returns:
        rx.Component: The Chat Sidebar Component.
    """
    return rx.el.div(
        rx.vstack(
            rx.hstack(
                rx.heading("ShitChat", size="6"),
                rx.heading("v1.0.0", size="3", class_name="text-gray-500"),
                spacing="0",
                align="baseline",
                justify="between",
                class_name="w-full mb-0",
            ),
            rx.heading("by Witty Wisterias", size="2", class_name="text-gray-400 -mt-4", spacing="0"),
            rx.divider(),
            rx.heading("Public Chat", size="2", class_name="text-gray-500"),
            rx.button(
                "Public Chat",
                color_scheme="teal",
                variant="surface",
                size="3",
                class_name="w-full justify-center bg-gray-100 hover:bg-gray-200",
                on_click=ChatState.select_chat("Public"),
            ),
            rx.divider(),
            rx.hstack(
                rx.heading("Private Chats", size="2", class_name="text-gray-500"),
                create_chat_component(
                    rx.button(
                        rx.icon("circle-plus", size=16, class_name="text-gray-500"),
                        class_name="bg-white",
                        on_click=ChatState.start_webcam,
                    )
                ),
                spacing="2",
                align="center",
                justify="between",
                class_name="w-full mb-0",
            ),
            rx.foreach(
                ChatState.chat_partners,
                lambda user_id: rx.button(
                    f"Private: {user_id}",
                    color_scheme="teal",
                    variant="surface",
                    size="3",
                    class_name="w-full justify-center bg-gray-100 hover:bg-gray-200",
                    on_click=ChatState.select_chat(user_id),
                ),
            ),
            rx.vstack(
                rx.heading(ProgressState.progress, size="2", class_name="text-gray-500"),
                rx.divider(),
                rx.hstack(
                    rx.hstack(
                        rx.avatar(
                            src=ChatState.user_profile_image, fallback=ChatState.user_id[:2], radius="large", size="3"
                        ),
                        rx.vstack(
                            rx.text(ChatState.user_name | ChatState.user_id, size="3"),  # type: ignore[operator]
                            rx.text(ChatState.user_id, size="1", class_name="text-gray-500"),
                            spacing="0",
                        ),
                    ),
                    user_info_component(),
                    spacing="2",
                    align="center",
                    justify="between",
                    class_name="mt-1 w-full",
                ),
                class_name="mt-auto mb-7 w-full",
            ),
            class_name="h-screen bg-gray-50",
        ),
        class_name="flex flex-col w-[340px] h-screen px-5 pt-3 mt-2 border-r border-gray-200",
    )
