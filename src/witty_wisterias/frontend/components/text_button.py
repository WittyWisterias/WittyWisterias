import reflex as rx

from frontend.states.chat_state import ChatState


def text_form() -> rx.Component:
    """
    Form for sending a text message.

    Returns:
        rx.Component: The Text form component.
    """
    return rx.vstack(
        rx.cond(
            ChatState.frame_data,
            rx.image(
                src=ChatState.frame_data,
                width="480px",
                alt="Live frame",
                border="2px solid teal",
                border_radius="16px",
            ),
            rx.hstack(
                rx.spinner(size="3"),
                rx.text(
                    "Loading Webcam image...",
                    color_scheme="gray",
                    size="5",
                ),
                align="center",
            ),
        ),
        rx.hstack(
            rx.dialog.close(
                rx.button(
                    "Cancel", variant="soft", color_scheme="gray", type="reset", on_click=ChatState.disable_webcam
                )
            ),
            rx.dialog.close(rx.button("Send", type="submit")),
        ),
        spacing="3",
        margin_top="16px",
    )


def send_text_component() -> rx.Component:
    """
    The dialog (and button) for sending texts.

    Returns:
        rx.Component: The Text Button Component, which triggers the Text Message Form.
    """
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.center(rx.text("Send Text")),
                padding="24px",
                radius="large",
                on_click=ChatState.start_webcam,
                width="100%",
            ),
        ),
        rx.dialog.content(
            rx.dialog.title("Send Text"),
            rx.dialog.description(
                "Send a text message to the chat by writing your message on a physical peace of paper and taking a"
                "picture of it with your webcam.",
                size="2",
                margin_bottom="16px",
            ),
            rx.dialog.description(
                "Your Webcam image is private and will not be shared in the chat.",
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
