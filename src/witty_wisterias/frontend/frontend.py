import reflex as rx

from frontend.components.chatapp import chat_app
from frontend.components.sidebar import chat_sidebar
from frontend.components.tos_accept_form import tos_accept_form
from frontend.states.chat_state import ChatState


@rx.page(on_load=ChatState.startup_event)
def index() -> rx.Component:
    """The main page of the chat application, which includes the sidebar and chat app components."""
    return rx.cond(
        ChatState.tos_accepted != "True",
        tos_accept_form(),
        rx.hstack(
            chat_sidebar(),
            chat_app(),
            size="2",
            class_name="overflow-hidden h-screen w-full",
        ),
    )
