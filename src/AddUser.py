import flet as ft
from database import add_new_user  # Ensure this function exists in database.py


def new_user(page: ft.Page):
    page.title = "Add User"
    page.window_height = 800
    page.window_width = 1280
    page.bgcolor = "#343434"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    username_field = ft.TextField(label="Username", bgcolor="#000000", width=156.5 * 3, height=25 * 3,color="white", border_color="white")
    password_field = ft.TextField(label="Password", password=True, bgcolor="#000000", width=156.5 * 3, height=25 * 3, color="white", border_color="white")
    level_field = ft.TextField(label="Level", bgcolor="#000000", width=156.5 * 3, height=25 * 3, color="white", border_color="white")

    selected_role = ft.Text("Student", color="blue", weight=ft.FontWeight.BOLD)

    def select_role(e):
        selected_role.value = e.control.content.content.value  # Accessing the Text widget correctly
        selected_role.color = "red" if selected_role.value == "Admin" else "blue"
        page.update()

    def role_menu_item(role, text_color, bg_color):
        return ft.PopupMenuItem(
            content=ft.Container(
                content=ft.Text(role, color=text_color, weight=ft.FontWeight.BOLD),
                padding=10,
                border_radius=10,
                bgcolor=bg_color,
                alignment=ft.alignment.center,
            ),
            on_click=select_role
        )

    role_button = ft.PopupMenuButton(
        content=selected_role,
        items=[
            role_menu_item("Admin", "white", "red"),
            role_menu_item("Student", "white", "blue"),
        ],
        bgcolor="#000000",
    )

    def submit_new_user(e):
        username = username_field.value.strip()
        password = password_field.value.strip()
        level = int(level_field.value) if level_field.value.isdigit() else 1
        role = selected_role.value

        if not username or not password:
            page.snack_bar = ft.SnackBar(content=ft.Text("Username and Password cannot be empty!", color="white"),
                                         bgcolor="red")
            page.snack_bar.open = True  # Correct way to show SnackBar
            page.update()
            return

        add_new_user(username, password, level, role)

        # Show a success SnackBar
        page.snack_bar = ft.SnackBar(content=ft.Text("User added successfully!", color="white"), bgcolor="green")
        page.snack_bar.open = True
        page.update()

        page.go("/account_management")

    # AppBar for navigation
    def app_bar():
        return ft.AppBar(
            title=ft.Text("Add New User", color="white"),
            bgcolor="#222222",
            actions=[
                ft.TextButton("Account Management", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/account_management")),
                ft.TextButton("Quiz Management", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/edit_page")),
                ft.TextButton("Profile", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/profile_management")),
                ft.TextButton("Logout", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/")),
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
                        ft.Row([password_field], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([level_field], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([role_button], alignment=ft.MainAxisAlignment.CENTER),
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

    # # Function to handle route changes
    # def route_change(route):
    #     page.views.clear()
    #     if page.route == "/add_new_user":
    #         page.views.append(add_user_view())
    #     elif page.route == "/account_management":
    #         page.views.append(account_management_view())
    #     page.update()
    #
    # # Set up route change handler
    # page.on_route_change = route_change

    # Navigate to the initial view
    # page.go("/add_new_user")


