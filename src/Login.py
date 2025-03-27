import platform
import time

import flet as ft
from database import user_info, last_Update, Chapter_Quiz, Add_ChapterDB, Add_QuizLVL, Add_Question
import SignIn
import os
from Menu import Menu
import json
import edit_Q3
import AdminAccountManagement
import Profile
import AddUser_Admin
import AddUser_Owner
import OwnerAccountManagement
import OwnerProfile
from dotenv import load_dotenv
import sys
import getpass

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


#Added Hashing
def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


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
        # Check if running as a PyInstaller executable
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS  # PyInstaller's temp extraction path
        else:
            base_path = os.path.dirname(__file__)  # Normal script execution path

        # 🛠 Developer-defined owner credentials (Set before deployment)
        ALLOWED_OWNER = "WONG JASON"  # Change to the correct username
        ALLOWED_HOSTNAME = "DESKTOP-RBGOM9O"  # Change to the real owner's device name

        # Get current system details
        current_user = getpass.getuser()  # Get current username
        current_hostname = platform.node()  # Get current device name
        dotenv_path = os.path.join(os.path.dirname(__file__), ".env")  # Get correct .env path

        # Debugging messages (Make sure this prints in CMD/terminal)
        print(f"🔍 Debug: Running as {current_user} on {current_hostname}")
        load_dotenv(dotenv_path)
        OWNER_KEY = None
        # 🛡️ Check if this system is the authorized owner
        if current_user == ALLOWED_OWNER and current_hostname == ALLOWED_HOSTNAME:
            print("✅ Access granted to owner. Setting file permissions...")
            # if os.name == "nt":  # Windows
            #     os.system(f'icacls "{dotenv_path}" /inheritance:r /grant "{current_user}:(R,W)" /deny Everyone')
            OWNER_KEY = os.getenv("OWNER_KEY")
            print("Test: ", OWNER_KEY)
        else:
            print(OWNER_KEY)

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
                page.views.append(SignIn.signin_view(page))
            elif page.route == "/edit_page":
                page.views.append(edit_Q3.main(page))
            elif page.route == "/stu_account_management":
                page.views.append(AdminAccountManagement.stu_account_management(page))
            elif page.route == "/profile_management":
                page.views.append(Profile.profile_management(page))
            elif page.route == "/add_new_stu":
                page.views.append(AddUser_Admin.new_student(page))
            elif page.route == "/admin_account_management":
                page.views.append(OwnerAccountManagement.admin_account_mkanagement(page))
            elif page.route == "/add_new_admin":
                page.views.append(AddUser_Owner.new_admin(page))
            elif page.route == "/owner_profile_management":
                page.views.append(OwnerProfile.owner_profile_management(page))
            else:
                page.views.append(login_view(page))

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
            hashed_password = hash_password(password)  # Hash the entered password
            print(hashed_password)
            if hashed_password:
                if hashed_password == OWNER_KEY:
                    print("🔑 Owner access granted via special key!")
                    page.go("/owner_profile_management")
                    return
            for i in user_info():  # Loop through stored user data
                stored_user = (i[1].strip(), i[3].strip())  # Strip DB values
                if (username, hashed_password) == stored_user:
                    print("✅ Correct Login!")
                    last_Update(i[0])
                    save_login_credentials(username, password)  # Password is hashed before saving
                    page.session.set("username", i[1])  # Store username
                    page.session.set("password", i[2])  # Store password
                    page.session.set("user_id", i[0])  # Store user ID for database update
                    # Run the Menu.py script
                    # subprocess.run([sys.executable, "Menu.py", str(i)])
                    if i[-3] == "Student":
                        page.window.close()
                        Menu(i)
                    elif i[-3] == "Admin":
                        # quiz = {
                        #     "1": [
                        #         ["Quiz Name",
                        #          "Description",
                        #          1,
                        #          "1",
                        #          {
                        #              "Question 1": [
                        #                  "A",
                        #                  "Option 1",
                        #                  "Option 2",
                        #                  "Option 3",
                        #                  "Option 4"
                        #              ]
                        #          }
                        #          ]
                        #     ]
                        # }
                        # if not os.path.exists("Quiz_draft.json"):
                        #     with open("Quiz_draft.json", "w") as file:
                        #         json.dump(quiz, file, indent=4)
                        if not Chapter_Quiz()[1]:
                            print("HAI")
                            Add_ChapterDB()
                            Add_QuizLVL(1, 1)
                            Add_Question(1)
                        page.go("/edit_page")
                    return
            print("Incorrect")

        page.go(page.route)


    ft.app(target=main)
