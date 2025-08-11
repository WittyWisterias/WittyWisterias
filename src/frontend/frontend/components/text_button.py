import reflex as rx

from frontend.states.chat_state import ChatState


def send_text_component() -> rx.Component:
    """The dialog (and button) for sending texts"""
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
            rx.form(
                rx.flex(
                    rx.text_area(
                        placeholder="Write your text here...",
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
                on_submit=ChatState.send_text,
                reset_on_submit=False,
            ),
        ),
    )
