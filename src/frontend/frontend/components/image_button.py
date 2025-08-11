import reflex as rx


def send_image_component() -> rx.Component:
    """The dialog (and button) for sending an image"""
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.center(rx.text("Send Image")),
                padding="24px",
                radius="large",
                flex=1,
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
