import os

from datetime import datetime, timedelta
import flet as ft
from database import select_user  # Ensure this function exists in database.py
from admin import AdminPage


def profile_management(page: ft.Page, role, audio1, audio2):
    user_id = page.session.get("user_id")

    # Retrieve user information from the database
    if role == "Admin":
        user_info = select_user(int(user_id[1:]), "Admin")
        username = user_info.Name
        email = user_info.Email
        reg_date = str(user_info.RegisteredDate)
        lastLogin_date = user_info.LastLogin
    elif role == "Owner":
        user_info = select_user(int(user_id[1:]), "Owner")
        print(" Owner", user_id)
        print(user_info)
        username = user_info.Name
        email = user_info.Email
        reg_date = str(user_info.RegisteredDate)
        lastLogin_date = user_info.LastLogin
    else:
        username = "N/A"
        email = "N/A"
        reg_date = "N/A"
        lastLogin_date = "N/A"

    Admin = AdminPage(page, role, audio1, audio2, "/profile_management")
    Hedr = Admin.hedrNavFdbkBx

    def time_ago(lastLogin_date):
        now = datetime.now()
        diff = now - lastLogin_date

        if diff < timedelta(minutes=1):
            return "Just now"
        elif diff < timedelta(hours=1):
            minutes = diff.seconds // 60
            return f"{minutes} min ago"
        elif diff < timedelta(days=1):
            hours = diff.seconds // 3600
            return f"{hours} hour ago" if hours == 1 else f"{hours} hours ago"
        else:
            days = diff.days
            return f"{days} day ago" if days == 1 else f"{days} days ago"

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
        value=str(time_ago(lastLogin_date)),
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
        route="/profile_management",
        padding=20,
        bgcolor="#343434",
        controls=
        [
            Admin.page.appbar,
            Hedr,
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
    )
