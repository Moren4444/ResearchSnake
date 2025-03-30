import platform
import subprocess
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
import re
import hashlib
import draft_page
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

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


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def load_login_credentials():
    """Load credentials from the JSON file."""
    if os.path.exists("user_credentials.json"):
        with open("user_credentials.json", "r") as file:
            return json.load(file)
    return {"username": "", "password": ""}  # Return empty values if file doesn't exist


username_error = ft.Text("", weight=ft.FontWeight.BOLD, size=15, color="red", visible=True)
password_error = ft.Text("", weight=ft.FontWeight.BOLD, size=15, color="red", visible=True)

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

        # Get current system details
        current_user = getpass.getuser()  # Get current username
        current_hostname = platform.node()  # Get current device name
        dotenv_path = os.path.join(os.getenv("APPDATA"), "Owner Store", ".env")  # Get correct .env path
        background_path = os.path.join(base_path, "assets", "Background_audio.mp3")
        audio1 = ft.Audio(
            src=background_path, autoplay=True
        )
        forest_image_path = os.path.join(base_path, "assets", "Forest.png")
        logo_path = os.path.join(base_path, "assets", "ResearchSnake.png")
        click_path = os.path.join(base_path, "assets", "Click_Audio.mp3")
        page.overlay.append(audio1)
        audio2 = ft.Audio(
            src=click_path,
            volume=1.0,  # Ensure the volume is high enough
            autoplay=False  # Prevent autoplay before the button click
        )
        page.overlay.append(audio2)

        def play_click_sound(e):
            if audio2 not in page.overlay:
                page.overlay.append(audio2)  # Add audio control first
                page.update()  # Ensure it's recognized by the UI
            audio2.play()  # Now play it

        # Debugging messages (Make sure this prints in CMD/terminal)
        print(f"🔍 Debug: Running as {current_user} on {current_hostname}")
        # 🛠 Developer-defined owner credentials (Set before deployment)
        # Change to the real owner's device name
        load_dotenv(dotenv_path)
        # ALLOWED_OWNER = os.getenv("ALLOWED_OWNER")
        # ALLOWED_HOSTNAME = os.getenv("ALLOWED_HOSTNAME")
        OWNER_KEY = None

        # 🛡️ Check if this system is the authorized owner
        def get_machine_id():
            try:
                # Get unique machine GUID (Windows)
                output = subprocess.check_output("wmic csproduct get uuid", shell=True)
                uuid = output.decode().split("\n")[1].strip()
                return uuid
            except:
                return None

        OWNER_KEY = os.getenv("OWNER_KEY")
        MACHINE_ID = os.getenv("MACHINE")

        def verify_machine_id(Machine_id, signed_machine_id):
            # Load the public key (bundled with the app)
            if not signed_machine_id:
                return False
            with open("public_key.pem", "rb") as f:
                Public_key = load_pem_public_key(f.read())

            # Compute the hash of the machine ID
            machine_id_hash = hashlib.sha256(Machine_id.encode()).digest()

            try:
                # Verify the signature
                Public_key.verify(
                    bytes.fromhex(signed_machine_id),
                    machine_id_hash,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                print("✅ Authorization successful: Machine ID is valid!")
                return True
            except:
                print("❌ Authorization failed: Machine ID is invalid!")
                return False
        USB_path = "D://private_key.pem"

        def sign_machine_id(Machine_id):
            # Load the private key (only the developer has this)
            if not os.path.exists(USB_path):
                return None
            with open(USB_path, "rb") as f:
                Private_key = load_pem_private_key(f.read(), password=None)

            # Create a secure hash of the Machine ID
            machine_id_hash = hashlib.sha256(Machine_id.encode()).digest()

            # Sign the hash
            signature = Private_key.sign(
                machine_id_hash,
                padding.PKCS1v15(),
                hashes.SHA256()
            )

            return signature.hex()  # Convert to a storable format

        if MACHINE_ID != hash_password(get_machine_id()):
            OWNER_KEY = None

        username_field = ft.TextField(
            label="Username",
            value=load_login_credentials().get("username", ""),
            bgcolor="#000000",
            width=156.5 * 3,
            color="#FFFFFF",
            border_radius=8,
            border_color="#FFFFFF",
        )

        password_field = ft.TextField(
            label="Password",
            value=load_login_credentials().get("password", ""),
            bgcolor="#000000",
            width=156.5 * 3,
            color="#FFFFFF",
            border_radius=8,
            password=True,
            can_reveal_password=True,
            border_color="#FFFFFF",
        )
        role = None

        # Create a container to hold the background image
        background_container = ft.Container(
            content=ft.Image(
                src=forest_image_path,  # Replace with your image path
                width=1525,
                height=800,
                fit=ft.ImageFit.COVER  # Ensure the image covers the entire space
            ),
            alignment=ft.alignment.center,
            expand=True  # Make the container expand to fill the available space
        )

        # Create a container to hold the Research Snake intro
        logo_container = ft.Container(
            # Load the Research Snake intro
            content=ft.Image(
                src=logo_path,
                width=300,
                height=300
            ),
            alignment=ft.alignment.top_center,
        )

        # Define a function to handle navigation
        def route_change(route):
            page.views.clear()
            nonlocal role

            if page.route == "/signin":
                page.views.append(SignIn.signin_view(page, play_click_sound))
            elif page.route == "/draft_page":
                page.views.append(draft_page.draft_page(page, audio1, audio2))
            elif page.route == "/edit_page":
                page.overlay.clear()
                page.views.append(edit_Q3.main(page, role, audio1, audio2))
            elif page.route == "/stu_account_management":
                page.views.append(AdminAccountManagement.stu_account_management(page, audio1, audio2))
            elif page.route == "/profile_management":
                page.views.append(Profile.profile_management(page, audio1, audio2))
            elif page.route == "/add_new_stu":
                page.views.append(AddUser_Admin.new_student(page, audio1, audio2))
            elif page.route == "/admin_account_management":
                page.views.append(OwnerAccountManagement.admin_account_management(page))
            elif page.route == "/add_new_admin":
                page.views.append(AddUser_Owner.new_admin(page))
            elif page.route == "/owner_profile_management":
                page.overlay.clear()
                page.views.append(OwnerProfile.owner_profile_management(page, role, audio1, audio2))
            else:
                page.views.append(login_view(page))

            page.update()

        page.on_route_change = route_change

        def login_view(pages):
            return ft.View(
                route="/",
                padding=0,  # Remove default view padding
                controls=[
                    ft.Stack(
                        [
                            background_container,  # Background image
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Container(
                                            content=ft.Column(
                                                [
                                                    logo_container,
                                                    username_field,  # Use the defined input field
                                                    ft.Column(
                                                        [username_error],
                                                        alignment=ft.alignment.center_left,
                                                        horizontal_alignment=ft.CrossAxisAlignment.START,
                                                        width=156.5 * 3
                                                    ),
                                                    password_field,
                                                    ft.Column(
                                                        [password_error],
                                                        alignment=ft.alignment.center_left,
                                                        horizontal_alignment=ft.CrossAxisAlignment.START,
                                                        width=156.5 * 3
                                                    ),
                                                    ft.ElevatedButton(
                                                        content=ft.Text("Login", color="white", size=25),
                                                        bgcolor="#35AD30",
                                                        width=84 * 3,
                                                        height=20 * 3,
                                                        # Call submit() on click
                                                        on_click=lambda e: [play_click_sound(e), submit(e)]
                                                    ),
                                                    ft.TextButton(
                                                        content=ft.Text("Sign Up", color="white", size=25),
                                                        on_click=lambda e: [play_click_sound(e),
                                                                            pages.go("/signin")]
                                                    )
                                                ],
                                                spacing=10,
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            )
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    expand=True,  # Critical for centering
                                )
                            )
                        ],
                        expand=True,  # Ensure the Stack expands to fill the view
                    )
                ]
            )

        # Function to handle button click

        def submit(e):
            nonlocal role
            # Reset all error labels
            username_error.value = ""
            password_error.value = ""

            # user_input = (username_field.value.strip(), password_field.value.strip())  # Remove spaces
            username = username_field.value.strip()
            password = password_field.value.strip()
            hashed_password = hash_password(password)  # Hash the entered password
            print(hashed_password)
            machine_id = get_machine_id()
            if hashed_password and verify_machine_id(machine_id, sign_machine_id(machine_id)):
                print("Accessing to owner")
                if hashed_password == OWNER_KEY:
                    role = "Owner"
                    print("🔑 Owner access granted via special key!")
                    page.go("/owner_profile_management")
                    return
            # Validate input
            if username == "":
                username_error.value = "Username is empty"

            if re.search(r'[^a-zA-Z0-9]', username):
                username_error.value = "Special characters not allowed"

            if password == "":
                password_error.value = "Password is empty"
                page.update()
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
                        role = "Admin"
                        if not Chapter_Quiz()[1]:
                            Add_ChapterDB()
                            Add_QuizLVL(1, 1)
                            Add_Question(1)
                        page.go("/edit_page")
                    return
            password_error.value = "Incorrect username or password"
            page.update()
            print("Incorrect")

        page.go(page.route)


    ft.app(target=main)
