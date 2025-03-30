from datetime import datetime

import flet as ft
from database import user_info, insert, get_last_user_Id
import os
import subprocess
import sys
import hashlib
import re


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


username = ft.TextField(
    label="Username",
    bgcolor="#000000",
    width=156.5 * 3,
    color="#FFFFFF",
    border_radius=8,
    border_color="#FFFFFF"
)
email = ft.TextField(
    label="Email",
    bgcolor="#000000",
    width=156.5 * 3,
    color="#FFFFFF",
    border_radius=8,
    border_color="#FFFFFF",
    suffix_text="@gmail.com"
)
password = ft.TextField(
    label="Password",
    bgcolor="#000000",
    width=156.5 * 3,
    color="#FFFFFF",
    border_radius=8,
    password=True,
    border_color="#FFFFFF"
)

confirm = ft.TextField(
    label="Confirm password",
    bgcolor="#000000",
    width=156.5 * 3,
    color="#FFFFFF",
    border_radius=8,
    password=True,
    can_reveal_password=True,
    border_color="#FFFFFF"
)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS  # PyInstaller's temp extraction path
else:
    base_path = os.path.dirname(__file__)  # Normal script execution path
forest_image_path = os.path.join(base_path, "assets", "Forest.png")
background = ft.Container(
    # Load the background image
    content=ft.Image(
        src=forest_image_path,  # Replace with your image path
        width=1525,
        height=800,
        fit=ft.ImageFit.COVER  # Ensure the image covers the entire space
    ),
    expand=True  # Make the container expand to fill the available space
)

username_error = ft.Text("", weight=ft.FontWeight.BOLD, size=15, color="red", visible=True,)
email_error = ft.Text("", weight=ft.FontWeight.BOLD, size=15, color="red", visible=True)
password_empty = ft.Text("", weight=ft.FontWeight.BOLD, size=15, color="red", visible=True)
confirm_password = ft.Text("", weight=ft.FontWeight.BOLD, size=15, color="red", visible=True)


def signin_view(page, click):
    for error_label in [username_error, email_error, password_empty, confirm_password]:
        error_label.value = ""
    return ft.View(
        route="/signin",
        padding=0,
        controls=[
            ft.Stack(
                [
                    background,
                    ft.Container(
                        expand=True,  # Allow it to take full screen space
                        content=ft.Column(
                            [
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            username,
                                            ft.Column(
                                                [username_error],
                                                alignment=ft.alignment.center_left,
                                                horizontal_alignment=ft.CrossAxisAlignment.START,
                                                width=156.5 * 3
                                            ),
                                            email,
                                            ft.Column(
                                                [email_error],
                                                alignment=ft.alignment.center_left,
                                                horizontal_alignment=ft.CrossAxisAlignment.START,
                                                width=156.5 * 3
                                            ),
                                            password,
                                            ft.Column(
                                                [password_empty],
                                                alignment=ft.alignment.center_left,
                                                horizontal_alignment=ft.CrossAxisAlignment.START,
                                                width=156.5 * 3
                                            ),
                                            confirm,
                                            ft.Column(
                                                [confirm_password],
                                                alignment=ft.alignment.center_left,
                                                horizontal_alignment=ft.CrossAxisAlignment.START,
                                                width=156.5 * 3
                                            ),
                                            ft.ElevatedButton(
                                                content=ft.Text("Sign Up", color="white", size=25),
                                                bgcolor="#35AD30",
                                                width=84 * 3,
                                                height=20 * 3,
                                                on_click=lambda e: [click(e), submit(e, page)]
                                            ),
                                            ft.TextButton(
                                                content=ft.Text("Login", color="white", size=25),
                                                on_click=lambda e: [click(e), page.go("/")]
                                            )
                                        ],
                                        spacing=10,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    alignment=ft.alignment.center,  # Center the login form
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,  # Center the entire column vertically
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Center horizontally
                            expand=True,  # Make it fill the screen
                        ),
                    )
                ],
                expand=True,
                alignment=ft.alignment.center
            )
        ]
    )


def submit(e, page):
    user_input = (username.value.strip(), password.value.strip(), confirm.value.strip(), email.value.strip())
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for error_label in [username_error, email_error, password_empty, confirm_password]:
        error_label.value = ""

    has_error = False
    if user_input[0] == "":
        username_error.value = "Username is required"
        has_error = True
    elif re.search(r'[^a-zA-Z0-9]', user_input[0]):
        username_error.value = "Special characters not allowed"
        has_error = True
    if user_input[2] == "":
        confirm_password.value = "Confirm password is required"
        has_error = True
    # Check if passwords match
    elif user_input[1] != user_input[2]:
        confirm_password.value = "Passwords do not match"
        has_error = True

    if user_input[1] == "":
        password_empty.value = "Password is required"
        has_error = True

    if user_input[3] == "":
        email_error.value = "Email is required"
        has_error = True
    elif re.search(r'[^a-zA-Z0-9]', user_input[3]):
        email_error.value = "Special characters not allowed"
        has_error = True
    # Check if username already exists
    for i in user_info():
        if user_input[0] == i[1]:
            username_error.value = "Username existed"
            has_error = True
        elif user_input[3] == i[2]:
            email_error.value = "Email existed"
            has_error = True

    if has_error:
        page.update()
        return

    last_user_id = get_last_user_Id()  # Implement this function in the database module
    new_id = str(int(last_user_id) + 1) if last_user_id else "1"  # Start from 1 if no users exist

    hashed_password = hash_password(user_input[1])  # Hash the password before storing

    # Insert new user into the database (storing hashed password)
    insert(f"INSERT INTO [User] VALUES ('{new_id}', '{user_input[0]}', '{user_input[-1]}@gmail.com', "
           f"'{hashed_password}', 1, 'Student', '{current_time}', '{current_time}')")

    print("✅ User registered successfully!")

    player_info = (new_id, user_input[0], hashed_password, 1, "Student")
    page.window.close()
    os.environ["PLAYER_LEVEL"] = "1"

    # Run the Menu.py script
    subprocess.run([sys.executable, "Menu.py", str(player_info)])
