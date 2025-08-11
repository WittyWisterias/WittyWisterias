import reflex as rx


def send_text_component() -> rx.Component:
    """The dialog (and button) for sending an texts"""
    # TODO: This should be replaced with the Webcam handler, text will do for now
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.center(rx.text("Send Text")),
                padding="24px",
                radius="large",
                flex=1,
            ),
        ),
        rx.dialog.content(
            rx.dialog.title("Send Text (TEMP)"),
            rx.dialog.description(
                "Send a text message to the chat. This is a temp feature until the webcam handler is implemented.",
                size="2",
                margin_bottom="16px",
            ),
            rx.text_area(placeholder="Write your text here..."),
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
