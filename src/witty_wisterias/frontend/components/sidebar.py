import reflex as rx

from frontend.states.progress_state import ProgressState


def chat_sidebar() -> rx.Component:
    """Sidebar component for the chat application, which allows users to select different chats."""
    return rx.el.div(
        rx.vstack(
            rx.hstack(
                rx.heading("Witty Wisterias", size="6"),
                rx.heading("v1.0.0", size="3", class_name="text-gray-500"),
                spacing="2",
                align="baseline",
                justify="between",
                class_name="w-full mb-0",
            ),
            rx.divider(),
            rx.heading("Public Chat", size="2", class_name="text-gray-500"),
            rx.button(
                "Public Chat",
                color_scheme="teal",
                variant="surface",
                size="3",
                class_name="w-full justify-center bg-gray-100 hover:bg-gray-200",
            ),
            rx.divider(),
            rx.heading("Private Chats", size="2", class_name="text-gray-500"),
            rx.button(
                "Private Chat 1",
                color_scheme="teal",
                variant="surface",
                size="3",
                class_name="w-full justify-center bg-gray-100 hover:bg-gray-200",
            ),
            rx.button(
                "Private Chat 2",
                color_scheme="teal",
                variant="surface",
                size="3",
                class_name="w-full justify-center bg-gray-100 hover:bg-gray-200",
            ),
            rx.vstack(
                rx.heading(ProgressState.progress, size="2", class_name="text-gray-500"),
                rx.divider(),
                rx.hstack(
                    rx.avatar(fallback="ID", radius="large", size="3"),
                    rx.vstack(
                        rx.text("User Name", size="3"),
                        rx.text("UserID", size="1", class_name="text-gray-500"),
                        spacing="0",
                    ),
                    class_name="mt-1",
                ),
                class_name="mt-auto mb-7 w-full",
            ),
            class_name="h-screen bg-gray-50",
        ),
        class_name="flex flex-col w-[340px] h-screen px-5 pt-3 mt-2 border-r border-gray-200",
    )
