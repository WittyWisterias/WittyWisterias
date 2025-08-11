import reflex as rx


def chat_sidebar() -> rx.Component:
    """Sidebar component for the chat application, which allows users to select different chats."""
    return rx.el.div(
        rx.vstack(
            rx.hstack(
                rx.heading("Witty Wisterias", size="6"),
                rx.heading("v1.0.0", size="3", class_name="text-gray-500"),
                spacing="2",
                align="baseline",
                justify="between",  # Überschriften an die Seiten verteilen
                class_name="w-full",
            ),
            rx.divider(),
            rx.heading("Public Chat", size="2", class_name="text-gray-500"),
            rx.button(
                "Public Chat",
                color_scheme="gray",
                variant="surface",
                size="3",
                class_name="w-full justify-center bg-gray-100 hover:bg-gray-200",
            ),
            rx.divider(),
            rx.heading("Private Chats", size="2", class_name="text-gray-500"),
            rx.button(
                "Private Chat 1",
                color_scheme="gray",
                variant="surface",
                size="3",
                class_name="w-full justify-center bg-gray-100 hover:bg-gray-200",
            ),
            rx.button(
                "Private Chat 2",
                color_scheme="gray",
                variant="surface",
                size="3",
                class_name="w-full justify-center bg-gray-100 hover:bg-gray-200",
            ),
            rx.hstack(
                rx.avatar(fallback="RX", radius="large", size="3"),
                rx.vstack(
                    rx.text("User Name", size="3"),
                    rx.text("UserID", size="1", class_name="text-gray-500"),
                    spacing="0",
                ),
                class_name="mt-auto mb-4",
            ),
            class_name="h-screen bg-gray-50",
        ),
        class_name="flex flex-col w-[320px] h-screen px-5 pt-3 border-r border-gray-200",
    )
