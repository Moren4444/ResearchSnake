import flet as ft
from database import stu_info  # Import user data from database
from Profile import profile_management


def account_management(page: ft.Page):
    users = stu_info()  # Fetch user data from database
    password_visible = False

    def toggle_password(e):
        nonlocal password_visible
        password_visible = not password_visible
        table.rows = create_rows()
        toggle_button.icon = ft.Icons.REMOVE_RED_EYE if password_visible else ft.Icons.REMOVE_RED_EYE_OUTLINED
        page.update()

    def create_rows():
        return [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(user[0]), color="white")),  # UserID
                    ft.DataCell(ft.Text(user[1], color="white")),  # Name
                    ft.DataCell(ft.Text(user[2] if password_visible else "******", color="white")),  # Password
                    ft.DataCell(ft.Text(str(user[3]), color="white")),  # Level
                ]
            ) for user in users
        ]

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("UserID", size=20, weight=ft.FontWeight.BOLD, color="white")),
            ft.DataColumn(ft.Text("Name", size=20, weight=ft.FontWeight.BOLD, color="white")),
            ft.DataColumn(ft.Text("Password", size=20, weight=ft.FontWeight.BOLD, color="white")),
            ft.DataColumn(ft.Text("Level", size=20, weight=ft.FontWeight.BOLD, color="white")),
        ],
        rows=create_rows(),
        bgcolor="#474747",
        border=ft.border.all(1, "white"),
        heading_row_color="#222222",
        data_row_color={"hovered": "#555555"},
    )

    toggle_button = ft.IconButton(
        icon=ft.Icons.REMOVE_RED_EYE if password_visible else ft.Icons.REMOVE_RED_EYE_OUTLINED,
        on_click=toggle_password,
        icon_color="white"
    )


    return ft.View(
            "/account_management",
            [
                ft.AppBar(
                    title=ft.Text("Account Management", color="white"),
                    bgcolor="#222222",
                    actions=[
                        ft.TextButton("Home", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/")),
                        ft.TextButton("Account Management", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/account_management")),
                        ft.TextButton("Quiz Management", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/edit_page")),
                        ft.TextButton("Profile", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/profile_management")),
                        ft.TextButton("Logout", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/")),
                    ],
                ),
                ft.Row([toggle_button, table], alignment=ft.MainAxisAlignment.CENTER),
            ],
            bgcolor="#343434"
        )
