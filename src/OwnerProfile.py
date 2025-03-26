import flet as ft
from database import update_user, select_user  # Ensure this function exists in database.py


def owner_profile_management(page: ft.Page):
    username = page.session.get("username")
    password = page.session.get("password")
    user_id = page.session.get("user_id")

    # Retrieve user information from the database
    # user_info = select_user(user_id)

    email = "Example@gmail.com"  #user_info.Email
    # reg_date = user_info.RegisteredDate
    # lastLogin_date = user_info.LastLogin

    username_field = ft.TextField(
        label="Username",
        value=username,
        read_only=True,
        bgcolor="#000000",
        width=156.5 * 3,
        height=25 * 3,
        color="white",
        border_color="white",
        label_style=ft.TextStyle(color="white"),
    )

    email_field = ft.TextField(
        label="Email Address",
        value=email,
        read_only=True,
        bgcolor="#000000",
        width=156.5 * 3,
        height=25 * 3,
        color="white",
        border_color="white",
        label_style=ft.TextStyle(color="white"),
    )

    # reg_date_field = ft.TextField(
    #     label="Registered Date",
    #     value=reg_date,
    #     read_only=True,
    #     bgcolor="#000000",
    #     width=156.5 * 3,
    #     height=25 * 3,
    #     color="white",
    #     border_color="white",
    #     label_style=ft.TextStyle(color="white"),
    # )

    # lastLogin_field = ft.TextField(
    #     label="Last Login",
    #     value=lastLogin_date,
    #     read_only=True,
    #     bgcolor="#000000",
    #     width=156.5 * 3,
    #     height=25 * 3,
    #     color="white",
    #     border_color="white",
    #     label_style=ft.TextStyle(color="white"),
    # )

    return ft.View(
        "/owner_profile_management",
        [
            ft.AppBar(
                title=ft.Text("Profile Management", color="white"),
                bgcolor="#222222",
                actions=[
                    ft.TextButton("Account Management", style=ft.ButtonStyle(color="white"),
                                  on_click=lambda e: page.go("/admin_account_management")),
                    ft.TextButton("Profile", style=ft.ButtonStyle(color="white"),
                                  on_click=lambda e: page.go("/owner_profile_management")),
                    ft.TextButton("Logout", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/")),
                ],
            ),
            ft.Container(
                content=ft.Column(
                    [
                        username_field,
                        email_field,
                        # reg_date_field,
                        # lastLogin_field,
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
