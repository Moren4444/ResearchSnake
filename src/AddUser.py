import os

import flet as ft
from database import add_new_user, user_info  # Ensure this function exists in database.py
from datetime import datetime


def new_user(page: ft.Page, role, audio1, audio2):
    page.title = "Add User"
    page.window_height = 800
    page.window_width = 1280
    page.bgcolor = "#343434"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    username_field = ft.TextField(label="Username", bgcolor="#000000", width=156.5 * 3, height=25 * 3,color="white", border_color="white", label_style=ft.TextStyle(color="white"))
    email_field = ft.TextField(label="Email Address", bgcolor="#000000", width=156.5 * 3, height=25 * 3,color="white", border_color="white", label_style=ft.TextStyle(color="white"))
    password_field = ft.TextField(label="Password", password=True, bgcolor="#000000", width=156.5 * 3, height=25 * 3, color="white", border_color="white", label_style=ft.TextStyle(color="white"))

    def submit_new_user(e):
        now = datetime.now()
        current_dt = now.strftime("%Y-%m-%d %H:%M:%S")

        username = username_field.value.strip()
        email = email_field.value.strip()
        password = password_field.value.strip()
        level = 100
        Role = "Admin" if role == "Owner" else "Student"
        registeredDate = current_dt
        lastLogin = current_dt

        if not username or not email or not password:
            page.snack_bar = ft.SnackBar(content=ft.Text("Username, email and password cannot be empty!", color="white"),
                                         bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        for i in user_info():
            if username == i[2]:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Username already exists!", color="white"),
                    bgcolor="red")
                page.snack_bar.open = True
                page.update()
                return

        add_new_user(username, email, password, level, Role, registeredDate, lastLogin)

        # Show a success SnackBar
        page.snack_bar = ft.SnackBar(content=ft.Text("User added successfully!", color="white"), bgcolor="green")
        page.snack_bar.open = True
        page.update()

        page.go("/account_management")

    draft = ft.TextButton("Draft", style=ft.ButtonStyle(color="white"),
                          on_click=lambda e: page.go("/draft_page"))
    if not os.path.exists("Quiz_draft2.json"):
        draft.disabled = True

    def app_bar():
        return ft.AppBar(
            title=ft.Text("Add New User", color="white"),
            bgcolor="#222222",
            actions=[
                *([draft] if role == "Admin" else []),
                ft.TextButton("Account Management", style=ft.ButtonStyle(color="white"),
                              on_click=lambda e: page.go("/account_management")),
                *([ft.TextButton("Quiz Management", style=ft.ButtonStyle(color="white"),
                                 on_click=lambda e: page.go("/edit_page"))] if role != "Owner" else []),
                ft.TextButton("Profile", style=ft.ButtonStyle(color="white"),
                              on_click=lambda e: page.go("/profile_management")),
                ft.TextButton("Logout", style=ft.ButtonStyle(color="white"), on_click=lambda e: [
                    page.overlay.append(audio1), page.overlay.append(audio2), page.go("/")]),
            ],
        )

    # def add_user_view():
    return ft.View(
        route="/add_new_user",
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


