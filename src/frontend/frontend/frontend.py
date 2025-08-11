import reflex as rx


class State(rx.State):
    """The app state."""


def send_image_dialog() -> rx.Component:
    """The dialog (and button) for sending an image"""
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.center(rx.text("Send Image")),
                padding="24px",
                radius="large",
            ),
        ),
        rx.dialog.content(
            rx.dialog.title("Send Image"),
            rx.dialog.description(
                "Send an image by describing it in the box below.",
                size="2",
                margin_bottom="16px",
            ),
            rx.text_area(placeholder="Describe it here..."),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        color_scheme="gray",
                        variant="soft",
                    ),
                ),
                rx.dialog.close(
                    rx.button("Send"),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
        ),
    )


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
                send_image_dialog(),
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
