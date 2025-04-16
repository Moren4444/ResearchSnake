import flet as ft
from database import add_new_student, add_new_admin, user_info
from datetime import datetime
from admin import AdminPage


def new_user(page: ft.Page, role, audio1, audio2):
    page.title = "Add User"
    page.window_height = 800
    page.window_width = 1280
    page.bgcolor = "#343434"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    Admin = AdminPage(page, role, audio1, audio2, "/add_new_user")
    Hedr = Admin.hedrNavFdbkBx

    # Common fields for both roles
    username_field = ft.TextField(label="Username", bgcolor="#000000", width=156.5 * 3, height=25 * 3, color="white",
                                  border_color="white", label_style=ft.TextStyle(color="white"))
    email_field = ft.TextField(label="Email Address", bgcolor="#000000", width=156.5 * 3, height=25 * 3, color="white",
                               border_color="white", label_style=ft.TextStyle(color="white"), prefix_text="",
                               suffix_text="@gmail.com")
    password_field = ft.TextField(label="Password", password=True, bgcolor="#000000", width=156.5 * 3, height=25 * 3,
                                  color="white", border_color="white", label_style=ft.TextStyle(color="white"))

    # Level field only for Admin
    level_field = ft.TextField(label="Level", bgcolor="#000000", width=156.5 * 3, height=25 * 3, color="white",
                               border_color="white",
                               label_style=ft.TextStyle(color="white")) if role == 'Admin' else None

    def submit_new_user(e):
        now = datetime.now()
        current_dt = now.strftime("%Y-%m-%d %H:%M:%S")

        username = username_field.value.strip()
        email = email_field.value.strip() + "@gmail.com"
        password = password_field.value.strip()
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

        # Create user after validation
        if role == "Owner":
            add_new_admin(username, email, password, registeredDate, lastLogin)
        elif role == "Admin":
            if not add_new_student(username, email, password, level, registeredDate, lastLogin):
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Username/Email already exists!", color="white"),
                    bgcolor="red",
                    duration=2000,
                )
                page.open(page.snack_bar)
                page.update()
            else:
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

