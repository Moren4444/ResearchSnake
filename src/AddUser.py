import flet as ft
from database import add_new_student, add_new_admin, check_existing
from datetime import datetime
from admin import AdminPage
import re
import hashlib


def new_user(page: ft.Page, role, audio1, audio2):
    page.title = "Add User"
    page.window_height = 800
    page.window_width = 1280
    page.bgcolor = "#343434"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    Admin = AdminPage(page, role, audio1, audio2, "/add_new_user")
    Hedr = Admin.hedrNavFdbkBx

    def hash_password(password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def on_change_user(e):
        value = e.control.value
        try:
            # Prevent typing anything ≤ 1
            if re.search(r'[^a-zA-Z0-9]', value):
                # Reset the value (clears the invalid input)
                e.control.value = value[:-1]
            e.control.update()
        except ValueError:
            pass  # Let NumbersOnlyInputFilter handle non-numeric characters

    # Common fields for both roles
    username_field = ft.TextField(label="Username", bgcolor="#000000", width=156.5 * 3, height=25 * 3, color="white",
                                  border_color="white", label_style=ft.TextStyle(color="white"),
                                  on_change=on_change_user)
    email_field = ft.TextField(label="Email Address", bgcolor="#000000", width=156.5 * 3, height=25 * 3, color="white",
                               border_color="white", label_style=ft.TextStyle(color="white"), prefix_text="",
                               suffix_text="@gmail.com")
    password_field = ft.TextField(label="Password", password=True, bgcolor="#000000", width=156.5 * 3, height=25 * 3,
                                  color="white", border_color="white", label_style=ft.TextStyle(color="white"))

    def on_change(e):
        value = e.control.value
        try:
            # Prevent typing anything ≤ 1
            if value and int(value) < 1:
                # Reset the value (clears the invalid input)
                e.control.value = ""
            e.control.update()
        except ValueError:
            pass  # Let NumbersOnlyInputFilter handle non-numeric characters

    # Level field only for Admin
    level_field = ft.TextField(label="Level", bgcolor="#000000", width=156.5 * 3, height=25 * 3, color="white",
                               border_color="white",
                               on_change=on_change,
                               input_filter=ft.NumbersOnlyInputFilter(),
                               label_style=ft.TextStyle(color="white")) if role == 'Admin' else None

    def submit_new_user(e):
        now = datetime.now()

        current_dt = now.strftime("%Y-%m-%d %H:%M:%S")

        if role == "Owner":
            username = "@" + username_field.value.strip()
        elif role == "Admin":
            username = username_field.value.strip()

        email = email_field.value.strip() + "@gmail.com"

        password = password_field.value.strip()
        hashed_password = hash_password(password)  # Hash the entered password
        print(hashed_password)

        level = level_field.value.strip() if role == 'Admin' else None

        Role = "Admin" if role == "Owner" else "Student"

        registeredDate = current_dt

        lastLogin = current_dt

        if not username or not email or not password:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Username, email and password cannot be empty!", color="white"),
                bgcolor="red",
                duration=2000,
            )

            page.open(page.snack_bar)
            page.update()
            return

        # Check for existing users
        # existing_users = user_info(role)
        # for user in existing_users:
        #     if username == user[2]:
        #         page.snack_bar = ft.SnackBar(
        #             content=ft.Text("Username already exists!", color="white"),
        #             bgcolor="red",
        #             duration=2000,
        #         )
        #         page.open(page.snack_bar)
        #         page.update()
        #         return
        #     elif email == user[3]:
        #
        #         return

        # Check if username or email already exists
        redundancy = check_existing(role, username, email)

        if not redundancy:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Username/Email already exists!", color="white"),
                bgcolor="red",
                duration=2000,
            )
            page.open(page.snack_bar)
            page.update()
        else:
            if role == "Owner":
                add_new_admin(username, email, hashed_password, registeredDate, lastLogin)
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("The user is added successfully!", color="white"),
                    bgcolor="green"
                )
            elif role == "Admin":
                if add_new_student(username, email, hashed_password, level, registeredDate, lastLogin):
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("The user is added successfully!", color="white"),
                        bgcolor="green"
                    )
            page.open(page.snack_bar)
            page.update()
            page.go("/account_management")

    # Build the column controls dynamically
    column_controls = [
        ft.Row([username_field], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([email_field], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([password_field], alignment=ft.MainAxisAlignment.CENTER)
    ]

    # Add level field row only for Admin role
    if role == 'Admin':
        column_controls.append(ft.Row([level_field], alignment=ft.MainAxisAlignment.CENTER))

    # Add the button row
    column_controls.append(
        ft.Row(
            [ft.ElevatedButton(
                text="Add User",
                on_click=submit_new_user,
                bgcolor="#4CAF50",
                color="white",
                width=200,
                height=40,
            )],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )

    return ft.View(
        route="/add_new_user",
        padding=20,
        bgcolor="#343434",
        controls=[
            Admin.page.appbar,
            Hedr,
            ft.Container(
                content=ft.Column(
                    column_controls,
                    spacing=20,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )
        ],
    )
