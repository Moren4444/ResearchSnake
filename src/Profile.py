import flet as ft
from database import update_user  # Ensure this function exists in database.py


def profile_management(page: ft.Page):
    # Retrieve user data from session
    username = page.session.get("username")
    password = page.session.get("password")
    user_id = page.session.get("user_id")

    if username is None:
        username = "Unknown"
    if password is None:
        password = "******"
    if user_id is None:
        user_id = None

    username_field = ft.TextField(
        label="Username",
        value=username,
        read_only=True,
        bgcolor="#000000",
        width=156.5 * 3,
        height=25 * 3,
        color="white",
        border_color="white",
    )

    password_field = ft.TextField(
        label="Password",
        value=password,
        read_only=False,
        password=True,
        can_reveal_password=True,
        bgcolor="#000000",
        width=156.5 * 3,
        height=25 * 3,
        color="white",
        border_color="white",
    )

    def save_changes(e):
        username = username_field.value
        new_password = password_field.value

        print(f"New Username: {username}")
        print(f"New Password: {new_password}")
        print(f"User ID: {user_id}")

        if user_id:
            try:
                update_user(user_id, username, new_password)
                print("Database update successful!")
                page.snack_bar = ft.SnackBar(
                    ft.Text("Changes saved successfully!", color="white"),
                    bgcolor="green",
                )
                page.snack_bar.open = True
            except Exception as ex:
                print(f"Error updating database: {ex}")  # Debugging
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"Error: {ex}", color="white"),
                    bgcolor="red",
                )
                page.snack_bar.open = True
            page.update()

    save_button = ft.ElevatedButton(
        text="Save",
        on_click=save_changes,
        bgcolor="#4CAF50",
        color="white",
    )

    return ft.View(
        "/profile_management",
        [
            ft.AppBar(
                title=ft.Text("Profile Management", color="white"),
                bgcolor="#222222",
                actions=[
                    ft.TextButton("Account Management", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/account_management")),
                    ft.TextButton("Quiz Management", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/edit_page")),
                    ft.TextButton("Profile", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/profile_management")),
                    ft.TextButton("Logout", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/")),
                ],
            ),
            ft.Container(
                content=ft.Column(
                    [
                        username_field,
                        password_field,
                        save_button,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
                alignment=ft.alignment.center,  # Center the container content
                expand=True,  # Make the container fill the available space
            ),
        ],
        bgcolor="#343434",
    )