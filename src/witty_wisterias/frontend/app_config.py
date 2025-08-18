import reflex as rx

app = rx.App(
    theme=rx.theme(appearance="light", has_background=True, radius="large", accent_color="teal"),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Bitcount+Prop+Single:slnt,wght@-8,600&display=swapp",
    ],
    style={
        "font_family": "Bitcount Prop Single",
        "background_color": "white",
    },
)
