import reflex as rx
from backend.message_format import MessageState

from frontend.components.chat_bubble import chat_bubble_component
from frontend.components.image_button import send_image_component
from frontend.components.text_button import send_text_component
from frontend.states.chat_state import ChatState


def chat_specific_messages(message: MessageState) -> rx.Component:
    """
    Returns the correct chat bubble if the message is for the selected chat.

    Args:
        message (Message): The Message object, which is to be determined if it fits the selected chat.

    Returns:
        rx.Component: A component representing the chat bubble for the message, if it fits.
    """
    # Storing Message/User Attributes for easier access
    user_id = message.get("user_id")
    receiver_id = message.get("receiver_id")
    selected_chat = ChatState.selected_chat

    return rx.cond(
        # Public Chat Messages
        (selected_chat == "Public") & (~receiver_id),
        chat_bubble_component(
            message["message"],
            rx.cond(message["user_name"], message["user_name"], user_id),
            user_id,
            message["user_profile_image"],
            message["own_message"],
            message["is_image_message"],
        ),
        rx.cond(
            # Private Chat Messages
            (selected_chat != "Public") & receiver_id & ((selected_chat == receiver_id) | (selected_chat == user_id)),
            chat_bubble_component(
                message["message"],
                rx.cond(message["user_name"], message["user_name"], user_id),
                user_id,
                message["user_profile_image"],
                message["own_message"],
                message["is_image_message"],
            ),
            # Fallback
            rx.fragment(),
        ),
    )


def chat_app() -> rx.Component:
    """
    Main chat application component.

    Returns:
        rx.Component: The main chat application component.
    """
    return rx.vstack(
        rx.heading(
            rx.cond(
                ChatState.selected_chat == "Public", "Public Chat", f"Private Chat with {ChatState.selected_chat}"
            ),
            spacing=0,
            size="6",
            align="center",
            class_name="text-gray-700 mt-4 w-full",
        ),
        rx.divider(),
        rx.auto_scroll(
            rx.foreach(
                ChatState.messages,
                lambda message: chat_specific_messages(message),
            ),
            class_name="flex flex-col gap-4 pb-6 pt-3 h-full w-full bg-gray-50 p-5 rounded-xl shadow-sm",
        ),
        rx.divider(),
        rx.hstack(
            rx.box(send_text_component(), width="50%"),
            rx.box(send_image_component(), width="50%"),
            spacing="2",
            class_name="mt-auto mb-3 w-full",
        ),
        spacing="4",
        class_name="h-screen w-full mx-5",
    )
