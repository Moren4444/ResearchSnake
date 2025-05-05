import platform
import threading
from threading import Event
import time

import flet as ft
from database import user_info, last_Update, Chapter_Quiz, Add_ChapterDB, Add_QuizLVL, Add_Question, update_DB
import SignIn
import os
from Menu import Menu
import json
import edit_Q3
import AccountManagement
import Profile
import AddUser
import getpass
import re
import hashlib
import draft_page
from OTP import send_otp_email as otp
from Resouce import resource_path


def delete_login_credentials():
    """Save hashed credentials to a JSON file."""
    update = load_login_credentials()
    update["username"] = ""
    update["password"] = ""
    with open("user_credentials.json", "w") as file:
        json.dump(update, file)


def save_login_credentials(username: str, password: str):
    """Save hashed credentials to a JSON file."""
    update = load_login_credentials()
    update["username"] = username
    update["password"] = password
    with open("user_credentials.json", "w") as file:
        json.dump(update, file)


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def load_login_credentials():
    """Load credentials from the JSON file."""
    try:
        if os.path.exists("user_credentials.json"):
            with open("user_credentials.json", "r") as file:
                return json.load(file)
        return {"username": "", "password": "", "img": ""}  # Return empty values if file doesn't exist
    except Exception as e:
        return {"username": "", "password": "", "img": ""}  # Return empty values if file doesn't exist


username_error = ft.Text("", weight=ft.FontWeight.BOLD, size=15, color="red", visible=True)
password_error = ft.Text("", weight=ft.FontWeight.BOLD, size=15, color="red", visible=True)
pin = None
count = 60
countdown_thread = None
countdown_event = Event()


def main(page: ft.Page):
    page.title = "Login"
    page.theme_mode = "dark"
    page.window.full_screen = True
    page.window.min_width = 1000
    page.window.min_height = 830

    def on_key(e: ft.KeyboardEvent):
        if e.key == "Escape":
            page.window.full_screen = False
            page.update()
        elif e.key == "F11":
            page.window.full_screen = True
            page.update()

    page.on_keyboard_event = on_key

    # Define input fields separately so they can be accessed
    # ✅ Apply styles at the start
    page.bgcolor = "#343434"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    background_path = resource_path("assets/Background_audio.mp3")
    audio1 = ft.Audio(
        src=background_path, autoplay=True
    )

    logo_path = resource_path("assets/ResearchSnake.png")
    click_path = resource_path("assets/Click_Audio.mp3")
    page.overlay.append(audio1)
    page.update()

    def restart_audio():
        print("Play again")
        audio1.play()
        threading.Timer(60, restart_audio).start()

    restart_audio()  # Start the looping

    audio2 = ft.Audio(
        src=click_path,
        volume=1.0,  # Ensure the volume is high enough
        autoplay=False  # Prevent autoplay before the button click
    )
    page.overlay.append(audio2)

    def play_click_sound(e=None):
        if audio2 not in page.overlay:
            page.overlay.append(audio2)  # Add audio control first
            page.update()  # Ensure it's recognized by the UI
        audio2.play()  # Now play it
        page.update()

    username_field = ft.TextField(
        label="Username",
        value=load_login_credentials().get("username", ""),
        bgcolor="#343434",
        color="#FFFFFF",
        label_style=ft.TextStyle(color="#04D9FF"),
        width=156.5 * 3,
        border_radius=8,
        border_color="#FFFFFF",
    )

    password_field = ft.TextField(
        label="Password",
        value=load_login_credentials().get("password", ""),
        bgcolor="#343434",
        width=156.5 * 3,
        label_style=ft.TextStyle(color="#04D9FF"),
        color="#FFFFFF",
        border_radius=8,
        password=True,
        border_color="#FFFFFF",
    )
    role = None
    admin_name = None
    # Create a container to hold the background image
    background_container = ft.Container(
        content=ft.Image(
            src=resource_path("assets/background.gif"),  # Replace with your image path
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

    def Forgot_pass(e):
        global pin, count, countdown_event, countdown_thread

        # Create a Text widget to update dynamically
        countdown_text = ft.Text(
            spans=[
                ft.TextSpan(
                    f"Resend {count}",
                    ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                    on_click=lambda e: resend_otp(e),
                )
            ]
        )

        def resend_otp(e):
            """Handle OTP resend request"""
            global count, countdown_event, countdown_thread
            print(countdown_thread)
            if countdown_thread and countdown_thread.is_alive():
                print("Stopping existing countdown")
                countdown_event.set()
                countdown_thread.join(timeout=1)
            # Stop any existing countdown

            countdown_event = Event()  # Create new event for new countdown

            # Reset count to 60
            count = 60
            countdown_text.spans[0].text = f"Resend {count}"
            page.update()

            # Show progress bar
            progress.visible = True
            page.update()

            # Send new OTP in background
            threading.Thread(target=send_otp, daemon=True).start()

            # Restart countdown
            countdown_thread = threading.Thread(target=update_countdown, daemon=True)
            countdown_thread.start()

        progress = ft.ProgressBar(visible=False, width=200)
        proceed = ft.ElevatedButton(content=ft.Text("Next", size=17),
                                    width=100, bgcolor="#35AD30",
                                    disabled=True)

        OTP = ft.TextField(
            label="OTP",
            input_filter=ft.NumbersOnlyInputFilter(),
            width=300 * 3,
            color="#FFFFFF",
            label_style=ft.TextStyle(color="#04D9FF"),
            border_radius=8,
            on_change=lambda e: update_button(e)
        )

        def update_button(e):
            done.disabled = not bool(OTP.value.strip())

        done = ft.ElevatedButton(
            content=ft.Text("Done", size=17),
            bgcolor="#35AD30",
            disabled=True,
            width=100
        )

        # OTP dialog
        otp_dialog = ft.AlertDialog(
            content=ft.Column(
                [
                    ft.Text("OTP"),
                    OTP,
                    countdown_text,
                    progress,
                    ft.Row([done], alignment=ft.MainAxisAlignment.END)
                ],
                height=160,
                width=300
            ),
            bgcolor="#544f4e"
        )

        def send_otp(e=None):
            """Function to send OTP in background"""
            global pin, count
            progress.visible = True
            page.update()

            try:
                pin = otp(email.value + "@gmail.com")
                print(pin)
            finally:
                progress.visible = False
                page.update()

        def update_button_state(e):
            proceed.disabled = not bool(email.value.strip())  # Disable if empty
            proceed.update()  # Refresh button state

        email = ft.TextField(
            label="Gmail",
            suffix_text="@gmail.com",
            width=300 * 3,
            label_style=ft.TextStyle(color="#04D9FF"),
            color="#FFFFFF",
            border_radius=8,
            on_change=update_button_state  # Trigger check on input change
        )

        email_dialog = ft.AlertDialog(
            content=ft.Column(
                [
                    ft.Text("Email"),
                    email,
                    progress,
                    ft.Row(controls=[
                        proceed,
                    ],
                        alignment=ft.MainAxisAlignment.END,
                        width=300
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
                width=300,
                height=120
            ),
            bgcolor="#544f4e"
        )

        def on_proceed(e):
            """Handle proceed button click"""
            global count, countdown_thread, countdown_event
            # Show progress immediately
            if countdown_thread and countdown_thread.is_alive():
                print("Stopping existing countdown")
                countdown_event.set()
                countdown_thread.join(timeout=1)

            progress.visible = True
            proceed.disabled = True
            if done:
                done.disabled = True
            page.update()
            count = 60
            countdown_event = Event()

            # Send OTP in background
            threading.Thread(target=send_otp, daemon=True).start()

            # Wait a moment to ensure progress shows
            time.sleep(3)

            # Open OTP dialog
            page.dialog = otp_dialog
            page.open(page.dialog)
            page.update()

            # Start countdown only if dialog is still open
            if page.dialog == otp_dialog:
                countdown_thread = threading.Thread(target=update_countdown, daemon=True)
                countdown_thread.start()

        def verify_otp(e):
            """Verify the entered OTP"""
            if pin:
                if str(OTP.value) == str(pin):
                    # Create password change dialog
                    password = ft.TextField(
                        width=300,
                        label="New Password",
                        label_style=ft.TextStyle(color="#04D9FF"),
                        password=True
                    )
                    confirm_password = ft.TextField(
                        width=300,
                        label="Confirm Password",
                        label_style=ft.TextStyle(color="#04D9FF"),
                        password=True
                    )

                    change_button = ft.ElevatedButton(
                        content=ft.Text("Change", size=17),
                        bgcolor="#35AD30",
                        width=100,
                        disabled=True
                    )

                    def validate_passwords(e):
                        change_button.disabled = not (
                                password.value and
                                password.value == confirm_password.value
                        )
                        page.update()

                    def change_password(e):
                        pass_value = hash_password(confirm_password.value)
                        [update_DB(f"UPDATE [{i}] SET [Password] = '{pass_value}' WHERE Email = "
                                   f"'{email.value}@gmail.com'") for i in ['Student', 'Admin', 'Owner']]

                        page.dialog = ft.AlertDialog(title=ft.Text("Password Changed", color="#FFFFFF"),
                                                     bgcolor="#544f4e")
                        page.close(change_dialog)
                        page.open(page.dialog)
                        page.update()

                    password.on_change = validate_passwords
                    confirm_password.on_change = validate_passwords
                    change_button.on_click = change_password

                    change_dialog = ft.AlertDialog(
                        content=ft.Column(
                            [
                                ft.Text("New Password"),
                                password,
                                ft.Text("Confirm Password"),
                                confirm_password,
                                ft.Row([change_button], alignment=ft.MainAxisAlignment.END)
                            ],
                            width=330,
                            height=200
                        ),
                        bgcolor="#544f4e"
                    )

                    page.dialog = change_dialog
                    page.open(page.dialog)
                    page.update()
                else:
                    OTP.error_text = "Invalid OTP"
                    page.update()
            else:
                OTP.error_text = "OTP Expired"
                page.update()

        # Assign event handlers
        proceed.on_click = on_proceed
        done.on_click = verify_otp

        # Open the dialog
        page.dialog = email_dialog
        page.open(page.dialog)
        page.update()

        # Function to update the countdown every second
        def update_countdown():
            global count, pin
            print(count)
            while count > 0 and not countdown_event.is_set():
                start_time = time.time()
                # Update count and UI
                count -= 1
                countdown_text.spans[0].text = f"Resend {count}" if count > 0 else "Resend OTP"
                page.update()

                # Precise 1-second sleep
                elapsed = time.time() - start_time
                time.sleep(max(0, 1 - int(elapsed)))
            pin = 0

    forgot_pass = ft.TextButton(
        content=ft.Container(
            content=ft.Text("Forgot Password", weight=ft.FontWeight.BOLD, size=17, color="#FFFFFF"),

        ),
        on_click=lambda e: Forgot_pass(e)
    )

    remember_me = ft.Checkbox(
        label="Remember Me",
        value=True if bool(load_login_credentials()["username"]) else False
    )

    # Define a function to handle navigation
    def route_change(route):
        page.views.clear()
        nonlocal role, admin_name
        print(admin_name)
        if page.route == "/signin":
            page.views.append(SignIn.signin_view(page, play_click_sound))
        elif page.route == "/draft_page":
            page.views.append(draft_page.draft_page(page, audio1, audio2))
        elif page.route == "/edit_page":
            page.overlay.clear()
            page.views.append(edit_Q3.main(page, role, audio1, audio2, admin_name))
        elif page.route == "/profile_management":
            page.overlay.clear()
            page.views.append(Profile.profile_management(page, role, audio1, audio2))
        elif page.route == "/add_new_user":
            page.views.append(AddUser.new_user(page, role, audio1, audio2))
        elif page.route == "/account_management":
            page.views.append(AccountManagement.account_management(page, role, audio1, audio2))
        else:
            page.views.append(login_view(page))

        page.update()

    page.on_route_change = route_change

    def login_view(pages):
        return ft.View(
            route="/",
            padding=0,  # Remove default view padding
            bgcolor="#000000",
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
                                                ft.Container(
                                                    content=ft.Column(
                                                        [
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
                                                            ft.Row(controls=[forgot_pass, remember_me],
                                                                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                                   width=156.5 * 3  # Ensure it has enough space
                                                                   ),
                                                            ft.ElevatedButton(
                                                                content=ft.Text("Login", color="#FFFFFF", size=25),
                                                                bgcolor="#35AD30",
                                                                width=84 * 3,
                                                                height=20 * 3,
                                                                # Call submit() on click
                                                                on_click=lambda e: [play_click_sound(e), submit(e)]
                                                            ),
                                                            ft.TextButton(
                                                                content=ft.Text("Sign Up", color="#FFFFFF", size=25),
                                                                on_click=lambda e: [play_click_sound(e),
                                                                                    pages.go("/signin")]
                                                            )
                                                        ],
                                                        spacing=10,
                                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                    ),
                                                    bgcolor=ft.Colors.with_opacity(0.5, "#909596"),
                                                    padding=20,
                                                    border_radius=10,
                                                )
                                            ],
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                        )
                                    ),
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
        # Validate input
        if username == "":
            username_error.value = "Username is empty"

        if password == "":
            password_error.value = "Password is empty"
            page.update()
            return
        role = "Owner" if username.startswith("#") else "Admin" if username.startswith("@") else "Student"

        for i in user_info(role):  # Loop through stored user data
            stored_user = (i[1].strip(), i[3].strip())  # Strip DB values
            if (username, hashed_password) == stored_user:
                print("✅ Correct Login!")
                last_Update(i[0], role)
                if not remember_me.value:
                    delete_login_credentials()
                elif remember_me.value:
                    save_login_credentials(username_field.value, password_field.value)

                # page.session.set("username", i[1])  # Store username
                # page.session.set("password", i[2])  # Store password
                page.session.set("user_id", i[0])  # Store user ID for database update
                # Run the Menu.py script
                # subprocess.run([sys.executable, "Menu.py", str(i)])
                if role == "Owner":
                    # owner_ID = i[0]
                    page.go("/profile_management")
                elif role == "Admin":
                    nonlocal admin_name
                    admin_name = i[1]
                    if not Chapter_Quiz()[1]:
                        Add_ChapterDB()
                        Add_QuizLVL(1, "CHA01")
                        Add_Question(1, i[1])
                    page.go("/edit_page")
                else:
                    page.window.close()
                    print("Student: ", i)
                    Menu(i)
                return
        if re.search(r'[^a-zA-Z0-9]', username):
            username_error.value = "Special characters not allowed"
        password_error.value = "Incorrect username or password"
        page.update()
        print("Incorrect")

    page.go(page.route)


if __name__ == "__main__":
    ft.app(target=main)
