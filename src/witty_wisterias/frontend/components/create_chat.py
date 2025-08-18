import reflex as rx

from frontend.states.chat_state import ChatState


def create_chat_component(create_chat_button: rx.Component, user_id: str | None = None) -> rx.Component:
    """
    The create-new-chat button, which spawns a dialog to create a new private chat.

    Args:
        create_chat_button (rx.Component): The Component which triggers the Create-Chat-Dialog.
        user_id (str | None): The UserID to default to.

    Returns:
        rx.Component: The Create Chat Form, with the create_chat_button as the trigger.
    """
    return rx.dialog.root(
        rx.dialog.trigger(create_chat_button),
        rx.dialog.content(
            rx.dialog.title("Create new Private Chat"),
            rx.dialog.description(
                "Create a new Private Chat with a user by entering their User ID.", size="2", margin_bottom="16px"
            ),
            rx.form(
                rx.vstack(
                    rx.input(
                        placeholder="Enter Receiver UserID",
                        default_value=user_id,
                        name="receiver_id",
                        required=True,
                        variant="surface",
                        class_name="w-full",
                    ),
                    rx.text_area(
                        placeholder="Write your first message...",
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
                ),
                on_submit=ChatState.send_private_text,
                reset_on_submit=False,
            ),
        ),
    )
