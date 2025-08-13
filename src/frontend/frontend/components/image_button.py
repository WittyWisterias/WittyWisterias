import reflex as rx

from frontend.states.chat_state import ChatState


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
                "Send an image by describing it in the box below. TEMP: You can post an image URL.",
                size="2",
                margin_bottom="16px",
            ),
            rx.form(
                rx.flex(
                    rx.text_area(
                        placeholder="Describe it here...",
                        size="3",
                        rows="5",
                        name="message",
                        required=True,
                        variant="surface",
                        class_name="w-full",
                    ),
                    rx.dialog.close(
                        rx.button(
                            "Cancel",
                            variant="soft",
                            color_scheme="gray",
                        ),
                    ),
                    rx.dialog.close(
                        rx.button("Send", type="submit"),
                    ),
                    spacing="3",
                    margin_top="16px",
                    justify="end",
                ),
                on_submit=ChatState.send_image,
                reset_on_submit=False,
            ),
        ),
    )
