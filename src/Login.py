import flet as ft
from database import user_info
import SignIn
import os
from Menu import Menu
import json
import edit_Q
import AccountManagement
import Profile
import hashlib


# def hash_password(password: str) -> str:
#     """Hash a password using SHA-256."""
#     return hashlib.sha256(password.encode()).hexdigest()
#

def save_login_credentials(username: str, password: str):
    """Save hashed credentials to a JSON file."""
    credentials = {
        "username": username,
        "password": password  # Store the hashed password
    }
    with open("user_credentials.json", "w") as file:
        json.dump(credentials, file)


def load_login_credentials():
    """Load credentials from the JSON file."""
    if os.path.exists("user_credentials.json"):
        with open("user_credentials.json", "r") as file:
            return json.load(file)
    return {"username": "", "password": ""}  # Return empty values if file doesn't exist


if __name__ == "__main__":

    def main(page: ft.Page):
        page.title = "Login"
        page.window.height = 800
        page.window.width = 1280
        # Define input fields separately so they can be accessed
        # ✅ Apply styles at the start
        page.bgcolor = "#343434"
        page.vertical_alignment = "center"
        page.horizontal_alignment = "center"

        username_field = ft.TextField(
            label="Username",
            value=load_login_credentials().get("username", ""),
            bgcolor="#000000",
            width=156.5 * 3,
            height=25 * 3,
            color="#FFFFFF",
            border_radius=8,
            border_color="#FFFFFF",
        )

        password_field = ft.TextField(
            label="Password",
            value=load_login_credentials().get("password", ""),
            bgcolor="#000000",
            width=156.5 * 3,
            height=25 * 3,
            color="#FFFFFF",
            border_radius=8,
            password=True,
            can_reveal_password=True,
            border_color="#FFFFFF",
        )

        # Define a function to handle navigation
        def route_change(route):
            page.views.clear()

            if page.route == "/signin":
                page.views.append(SignIn.signin_view(page))  # Load Sign-In Page
            elif page.route == "/edit_page":
                page.views.append(edit_Q.main(page))
            elif page.route == "/account_management":  # ✅ Handle Account Management navigation
                page.views.append(AccountManagement.account_management(page))
            elif page.route == "/profile_management":  # ✅ Handle Account Management navigation
                page.views.append(Profile.profile_management(page))
            else:
                page.views.append(login_view(page))  # Load Login Page

            page.update()

        page.on_route_change = route_change

        def login_view(pages):
            return ft.View(
                route="/",
                padding=0,  # Remove default view padding
                bgcolor="#343434",  # Set background color for the view
                controls=[
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Row(
                                                [ft.Text("Login", size=30, weight=ft.FontWeight.BOLD, color="white",
                                                         italic=True)],
                                                alignment=ft.MainAxisAlignment.START,
                                            ),
                                            username_field,  # Use the defined input fields
                                            password_field,
                                            ft.ElevatedButton(
                                                content=ft.Text("Enter", color="White", size=20),
                                                bgcolor="#FF0066",
                                                width=84 * 3,
                                                height=20 * 3,
                                                on_click=submit,  # Call submit() on click
                                            ),
                                            ft.TextButton("Sign up", style=ft.ButtonStyle(color="white"),
                                                          on_click=lambda e: pages.go("/signin")),
                                        ],
                                        spacing=20,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    width=187 * 3,
                                    height=156 * 3,
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

        # Function to handle button click
        def submit(e):
            # user_input = (username_field.value.strip(), password_field.value.strip())  # Remove spaces
            username = username_field.value.strip()
            password = password_field.value.strip()
            for i in user_info():  # Loop through stored user data
                stored_user = (i[1].strip(), i[2].strip())  # Strip DB values
                if (username, password) == stored_user:
                    print("✅ Correct Login!")
                    save_login_credentials(username, password)  # Password is hashed before saving

                    # Run the Menu.py script
                    # subprocess.run([sys.executable, "Menu.py", str(i)])
                    if i[-1] == "Student":
                        page.window.close()
                        Menu(i)
                    else:
                        print("Admin")
                        page.go("/edit_page")
                    return
            print("Incorrect")

        page.go(page.route)


    ft.app(target=main)
