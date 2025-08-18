import reflex as rx

from frontend.states.chat_state import ChatState


def image_form() -> rx.Component:
    """
    Form for sending an image message.

    Returns:
        rx.Component: The Image form component.
    """
    return rx.vstack(
        rx.text_area(
            placeholder="Describe it here...",
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


def send_image_component() -> rx.Component:
    """
    The dialog (and button) for sending an image

    Returns:
        rx.Component: The Image Button Component, which triggers the Image Message Form.
    """
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.center(rx.text("Send Image")),
                padding="24px",
                radius="large",
                width="100%",
            ),
        ),
        rx.dialog.content(
            rx.dialog.title("Send Image"),
            rx.dialog.description(
                "Send an image by describing it in the box below. It will be generated using AI and sent to the chat.",
                size="2",
                margin_bottom="16px",
            ),
            rx.cond(
                ChatState.selected_chat == "Public",
                rx.form(
                    image_form(),
                    on_submit=ChatState.send_public_image,
                ),
                rx.form(
                    image_form(),
                    on_submit=ChatState.send_private_image,
                ),
            ),
        ),
    )
