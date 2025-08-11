import reflex as rx


class State(rx.State):
    """The app state."""


def index() -> rx.Component:
    """Welcome Page (Index)"""
    return rx.container(
        rx.vstack(
            rx.aspect_ratio(
                rx.box(
                    border_radius="6px",
                    class_name="border border-2 border-gray-500",
                    width="100%",
                    height="100%",
                ),
                ratio=1,
            ),
            rx.grid(
                rx.button(
                    rx.center(rx.text("Send Text")),
                    padding="24px",
                    radius="large",
                ),
                rx.button(
                    rx.center(rx.text("Send Image")),
                    padding="24px",
                    radius="large",
                ),
                class_name="w-full",
                columns="2",
                spacing="4",
            ),
            class_name="w-full",
        ),
        size="2",
    )


app = rx.App()
app.add_page(index)
