import reflex as rx

from frontend.components.chatapp import chat_app
from frontend.components.sidebar import chat_sidebar


def index() -> rx.Component:
    """The main page of the chat application, which includes the sidebar and chat app components."""
    return rx.hstack(
        chat_sidebar(),
        chat_app(),
        size="2",
        class_name="overflow-hidden h-screen w-full",
    )


app = rx.App(
    theme=rx.theme(appearance="light", has_background=True, radius="large", accent_color="teal"),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Bitcount+Prop+Single:slnt,wght@-8,600&display=swapp",
    ],
    style={
        "font_family": "Bitcount Prop Single",
    },
)
app.add_page(index)
