import reflex as rx

from frontend.states.chat_state import ChatState


def user_info_component() -> rx.Component:
    """
    The dialog (and button) for editing the user information.

    Returns:
        rx.Component: The User Info Edit Button, which triggers the User Info Edit Form.
    """
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(rx.icon("user-pen", size=25, class_name="text-gray-500"), class_name="bg-white")),
        rx.dialog.content(
            rx.dialog.title("Edit your User Information"),
            rx.dialog.description(
                "Here you can edit your user information, including your username and profile picture.",
                size="2",
                margin_bottom="16px",
            ),
            rx.form(
                rx.vstack(
                    rx.input(
                        placeholder="Enter your new Username",
                        default_value=ChatState.user_name,
                        name="user_name",
                        required=True,
                        variant="surface",
                        class_name="w-full",
                    ),
                    rx.input(
                        placeholder="Enter your new Profile Picture URL",
                        name="user_profile_image",
                        variant="surface",
                        class_name="w-full",
                    ),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button(
                                "Cancel",
                                variant="soft",
                                color_scheme="gray",
                            )
                        ),
                        rx.dialog.close(
                            rx.button("Send", type="submit"),
                        ),
                    ),
                    spacing="3",
                    margin_top="16px",
                    justify="end",
                ),
                on_submit=ChatState.edit_user_info,
            ),
        ),
    )
