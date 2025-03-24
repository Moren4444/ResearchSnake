import flet as ft
from database import user_info, insert, get_last_user_Id
import os
import subprocess
import sys
from Menu import Menu

username = ft.TextField(
    label="Username",
    bgcolor="#000000",
    width=156.5 * 3,
    height=25 * 3,
    color="#FFFFFF",
    border_radius=8,
    border_color="#FFFFFF"
)
password = ft.TextField(
    label="Password",
    bgcolor="#000000",
    width=156.5 * 3,
    height=25 * 3,
    color="#FFFFFF",
    border_radius=8,
    password=True,
    border_color="#FFFFFF")

confirm = ft.TextField(
    label="Confirm password",
    bgcolor="#000000",
    width=156.5 * 3,
    height=25 * 3,
    color="#FFFFFF",
    border_radius=8,
    password=True,
    can_reveal_password=True,
    border_color="#FFFFFF"
)


def signin_view(page):
    return ft.View(
        route="/signin",
        bgcolor="#343434",
        controls=[
            ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [ft.Text("Sign in", size=30, weight=ft.FontWeight.BOLD, color="white",
                                                 italic=True)],
                                        alignment=ft.MainAxisAlignment.START,
                                    ),
                                    username,
                                    password,
                                    confirm,
                                    ft.ElevatedButton(
                                        content=ft.Text("Enter", color="White", size=20),
                                        bgcolor="#FF0066",
                                        width=84 * 3,
                                        height=20 * 3,
                                        on_click=lambda e: submit(e, page),  # Call submit() on click
                                    ),
                                    ft.TextButton("Login", style=ft.ButtonStyle(color="white"),
                                                  on_click=lambda e: page.go("/")),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            width=187 * 3,
                            height=176 * 3,
                            padding=50,
                            border_radius=20,
                            bgcolor="#474747",
                            shadow=ft.BoxShadow(
                                offset=(0, 4),
                                color=ft.colors.with_opacity(0.2, "black"),
                                blur_radius=4,
                                spread_radius=3,
                            ),
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,  # Critical for centering
                ),
                expand=True,  # Critical for centering
                alignment=ft.alignment.center,
            )
        ]
    )


def submit(e, page):
    user_input = (username.value.strip(), password.value.strip(), confirm.value.strip())
    if user_input[1] != user_input[2]:
        print("Password must be the same")
        return
    for i in user_info():
        if user_input[0] == i[1]:
            print("Username already exists")
            return

    last_user_id = get_last_user_Id()  # Implement this function
    if last_user_id:
        new_id = str(int(last_user_id) + 1)  # Increment
    else:
        new_id = "1"  # Start with 1 if no users exist

    # Insert new user into the database
    insert(f"INSERT INTO [User] VALUES ('{new_id}', '{user_input[0]}', '{user_input[1]}', 1, 'Student', 1)")
    print("User registered successfully!")
    player_info = tuple([new_id, user_input[0], user_input[1], 1, "Student"])
    page.window.close()
    os.environ["PLAYER_LEVEL"] = "1"
    # Run the Menu.py script
    # subprocess.run([sys.executable, "Menu.py", str(player_info)])
    Menu(player_info)
    return
