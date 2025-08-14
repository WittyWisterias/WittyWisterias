import reflex as rx

from frontend.states.chat_state import ChatState


def tos_accept_form() -> rx.Component:
    """Terms of Service Accept Form"""
    return rx.form(
        rx.vstack(
            rx.text("You hereby accept the Terms of Service of:"),
            rx.hstack(
                rx.link("freeocr.ai", href="https://freeocr.ai/terms-of-service"),
                rx.link("aihorde.net", href="https://aihorde.net/terms"),
                rx.link("freeimghost.net", href="https://freeimghost.net/page/tos"),
                align="center",
                justify="center",
            ),
            rx.button("Accept", type="submit"),
            align="center",
            justify="center",
        ),
        on_submit=lambda _: ChatState.accept_tos(),
        class_name="p-4 bg-gray-100 rounded-lg shadow-md w-screen h-screen flex items-center justify-center",
    )
