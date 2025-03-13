import flet as ft
from database import user_info  # Import user data from database


def profile_management(page: ft.Page):
    # Fetch user data (assuming user_info() returns a list with username and password)
    user_data = user_info()  # Example: user_data = ["username", "password"]

    # Create text fields for username and password
    username_field = ft.TextField(
        label="Username",
        value=user_data[1],  # Display the stored username
        read_only=False,  # Make the field editable
        bgcolor="#000000",
        width=156.5 * 3,
        height=25 * 3,
        color="white",
        border_color="white",
    )

    password_field = ft.TextField(
        label="Password",
        value=user_data[2],  # Display the stored password
        read_only=True,  # Make the field read-only
        password=True,  # Hide the password with asterisks
        can_reveal_password=False,  # Disable the reveal password option
        bgcolor="#000000",
        width=156.5 * 3,
        height=25 * 3,
        color="white",
        border_color="white",
    )

    return ft.View(
            "/profile_management",
            [
                ft.AppBar(
                    title=ft.Text("Profile Management", color="white"),
                    bgcolor="#222222",
                    actions=[
                        ft.TextButton("Home", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/")),
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
