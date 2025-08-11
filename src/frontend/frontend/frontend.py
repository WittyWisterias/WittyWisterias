import reflex as rx

from frontend.components.chatapp import chat_app
from frontend.components.sidebar import chat_sidebar


def index() -> rx.Component:
    """The main page of the chat application, which includes the sidebar and chat app components."""
    return rx.hstack(
        chat_sidebar(),
        chat_app(),
        size="2",
    )


app = rx.App(theme=rx.theme(appearance="light", has_background=True, radius="large", accent_color="teal"))
app.add_page(index)
