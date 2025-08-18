import reflex as rx

from frontend.states.chat_state import ChatState


def text_form() -> rx.Component:
    """
    Form for sending a text message.

    Returns:
        rx.Component: The Text form component.
    """
    return rx.vstack(
        rx.text_area(
            placeholder="Write your text here...",
            size="3",
            rows="5",
            name="message",
            required=True,
            variant="surface",
            class_name="w-full",
        ),
        rx.hstack(
            rx.dialog.close(rx.button("Cancel", variant="soft", color_scheme="gray")),
            rx.dialog.close(rx.button("Send", type="submit")),
        ),
        spacing="3",
        margin_top="16px",
        justify="end",
    )


def send_text_component() -> rx.Component:
    """
    The dialog (and button) for sending texts.

    Returns:
        rx.Component: The Text Button Component, which triggers the Text Message Form.
    """
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
            rx.cond(
                ChatState.selected_chat == "Public",
                rx.form(
                    text_form(),
                    on_submit=ChatState.send_public_text,
                ),
                rx.form(
                    text_form(),
                    on_submit=ChatState.send_private_text,
                ),
            ),
        ),
    )
