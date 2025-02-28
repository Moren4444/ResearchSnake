import flet as ft
from database import user_info
import SignIn


def main(page: ft.Page):
    page.title = "Login"
    # Define input fields separately so they can be accessed
    # ✅ Apply styles at the start
    page.bgcolor = "#343434"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    username_field = ft.TextField(
        label="Username",
        bgcolor="#000000",
        width=156.5 * 3,
        height=25 * 3,
        color="#FFFFFF",
        border_radius=8,
        border_color="#FFFFFF",
    )

    password_field = ft.TextField(
        label="Password",
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
        user_input = (username_field.value.strip(), password_field.value.strip())  # Remove spaces
        for i in user_info():  # Loop through stored user data
            stored_user = (i[1].strip(), i[2].strip())  # Strip DB values

            if user_input == stored_user:
                print("✅ Correct Login!")
                return
        print("Incorrect")

    page.go(page.route)


ft.app(target=main)
