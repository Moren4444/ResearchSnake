import hashlib

import flet as ft
from database import add_new_user  # Ensure this function exists in database.py
from datetime import datetime


def new_admin(page: ft.Page):
    page.title = "Add User"
    page.window_height = 800
    page.window_width = 1280
    page.bgcolor = "#343434"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    username_field = ft.TextField(label="Username", bgcolor="#000000", width=156.5 * 3, height=25 * 3,color="white", border_color="white")
    email_field = ft.TextField(label="Email Address", bgcolor="#000000", width=156.5 * 3, height=25 * 3,color="white", border_color="white")
    password_field = ft.TextField(label="Password", password=True, bgcolor="#000000", width=156.5 * 3, height=25 * 3, color="white", border_color="white")
    level_field = ft.TextField(label="Level", bgcolor="#000000", width=156.5 * 3, height=25 * 3, color="white", border_color="white")

    def submit_new_user(e):
        now = datetime.now()
        current_dt = now.strftime("%Y-%m-%d %H:%M:%S")

        username = username_field.value.strip()
        email = email_field.value.strip()
        password = password_field.value.strip()
        hash_pass = hashlib.sha256(password.encode()).hexdigest()
        level = int(level_field.value) if level_field.value.isdigit() else 1
        role = "Admin"
        registeredDate = current_dt
        lastLogin = current_dt

        if not username or not email or not password:
            page.snack_bar = ft.SnackBar(content=ft.Text("Username, email and password cannot be empty!", color="white"),
                                         bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        add_new_user(username, email, hash_pass, level, role, registeredDate, lastLogin)

        # Show a success SnackBar
        page.snack_bar = ft.SnackBar(content=ft.Text("User added successfully!", color="white"), bgcolor="green")
        page.snack_bar.open = True
        page.update()

        page.go("/admin_account_management")

    def app_bar():
        return ft.AppBar(
            title=ft.Text("Add New User", color="white"),
            bgcolor="#222222",
            actions=[
                ft.TextButton("Account Management", style=ft.ButtonStyle(color="white"),
                              on_click=lambda e: page.go("/admin_account_management")),
                ft.TextButton("Profile", style=ft.ButtonStyle(color="white"),
                              on_click=lambda e: page.go("/owner_profile_management")),
                ft.TextButton("Logout", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/")),
            ],
        )

    # def add_user_view():
    return ft.View(
        route="/add_new_admin",
        padding=20,
        bgcolor="#343434",
        appbar=app_bar(),
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row([username_field], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([email_field], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([password_field], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([level_field], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    text="Add User",
                                    on_click=submit_new_user,
                                    bgcolor="#4CAF50",
                                    color="white",
                                    width=200,
                                    height=40,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,  # Centering the button
                        ),
                    ],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.CENTER,  # Center all elements inside the column
                ),
                alignment=ft.alignment.center,
                expand=True,
            )
        ],
    )


