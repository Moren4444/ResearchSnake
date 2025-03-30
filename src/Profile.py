import os

import flet as ft
from database import update_user, select_user  # Ensure this function exists in database.py


def profile_management(page: ft.Page, audio1, audio2):
    username = page.session.get("username")
    password = page.session.get("password")
    user_id = page.session.get("user_id")

    # Retrieve user information from the database
    user_info = select_user(user_id)

    if user_info:
        email = user_info.Email
        reg_date = user_info.RegisteredDate
        lastLogin_date = user_info.LastLogin
    else:
        email = "N/A"
        reg_date = "N/A"
        lastLogin_date = "N/A"

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

    reg_date_field = ft.TextField(
        label="Registered Date",
        value=reg_date,
        read_only=True,
        bgcolor="#000000",
        width=156.5 * 3,
        height=25 * 3,
        color="white",
        border_color="white",
        label_style=ft.TextStyle(color="white"),
    )

    lastLogin_field = ft.TextField(
        label="Last Login",
        value=lastLogin_date,
        read_only=True,
        bgcolor="#000000",
        width=156.5 * 3,
        height=25 * 3,
        color="white",
        border_color="white",
        label_style=ft.TextStyle(color="white"),
    )

    draft = ft.TextButton("Draft", style=ft.ButtonStyle(color="white"),
                          on_click=lambda e: page.go("/draft_page"))
    if not os.path.exists("Quiz_draft2.json"):
        draft.disabled = True
    return ft.View(
        "/profile_management",
        [
            ft.AppBar(
                title=ft.Text("Profile Management", color="white"),
                bgcolor="#222222",
                actions=[
                    draft,
                    ft.TextButton("Account Management", style=ft.ButtonStyle(color="white"),
                                  on_click=lambda e: page.go("/stu_account_management")),
                    ft.TextButton("Quiz Management", style=ft.ButtonStyle(color="white"),
                                  on_click=lambda e: page.go("/edit_page")),
                    ft.TextButton("Profile", style=ft.ButtonStyle(color="white"),
                                  on_click=lambda e: page.go("/profile_management")),
                    ft.TextButton("Logout", style=ft.ButtonStyle(color="white"),
                                  on_click=lambda e: [page.overlay.append(audio1), page.overlay.append(audio2),
                                                      page.go("/")]),
                ],
            ),
            ft.Container(
                content=ft.Column(
                    [
                        username_field,
                        email_field,
                        reg_date_field,
                        lastLogin_field,
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