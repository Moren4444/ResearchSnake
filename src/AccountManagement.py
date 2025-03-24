import flet as ft
from database import profile_info, update_user_role, delete_user


def account_management(page: ft.Page):
    users = profile_info()
    password_visible = False

    def toggle_password(e):
        nonlocal password_visible
        password_visible = not password_visible
        table.rows = create_rows()
        toggle_button.icon = ft.Icons.REMOVE_RED_EYE if password_visible else ft.Icons.REMOVE_RED_EYE_OUTLINED
        page.update()

    def edit_role_dialog(user_id):
        print(f"Editing role for user ID: {user_id}")

        def save_role(e):
            new_role = role_dropdown.value
            print(f"New role: {new_role}")
            update_user_role(user_id, new_role)

            nonlocal users
            users = profile_info()  # Refresh the list
            print(users)
            table.rows = create_rows()
            role_dropdown.value = users[user_id - 1][5]
            role_dropdown.update()
            page.go("/account_management")
            page.close(edit_role)

        role_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("Admin"),
                ft.dropdown.Option("Student"),
            ],
            value=users[user_id - 1][5],
        )

        edit_role = ft.AlertDialog(
            title=ft.Text("Edit User Role"),
            content=role_dropdown,
            actions=[ft.TextButton("Save", on_click=save_role)],
        )
        page.open(edit_role)
        page.update()

    # Delete User Function
    def delete_user_action(user_id):
        print(f"Attempting to delete user with ID: {user_id}")

        def confirm_delete(e):
            nonlocal users
            delete_user(user_id)
            users = profile_info()
            table.rows = create_rows()
            page.go("/account_management")
            page.close(delete_accDialog)

        delete_accDialog = ft.AlertDialog(
            title=ft.Text("Confirm Deletion"),
            content=ft.Text("Are you sure you want to delete this user?"),
            actions=[
                ft.TextButton("Delete", on_click=confirm_delete),
                ft.TextButton("Cancel", on_click=lambda e: page.close(delete_accDialog)),
            ],
        )
        page.open(delete_accDialog)
        page.update()

    # # Add New User Function
    # def add_user_dialog(e):
    #     def submit_new_user(e):
    #         username = username_field.value
    #         password = password_field.value
    #         level = level_field.value
    #         role = role_dropdown.value
    #         add_user(username, password, level, role)
    #         page.go("/account_management")  # Refresh Page
    #
    #     username_field = ft.TextField(label="Username")
    #     password_field = ft.TextField(label="Password", password=True)
    #     level_field = ft.TextField(label="Level")
    #     role_dropdown = ft.Dropdown(
    #         options=[
    #             ft.dropdown.Option("Admin"),
    #             ft.dropdown.Option("Student"),
    #         ],
    #         value="Student",
    #     )
    #
    #     page.dialog = ft.AlertDialog(
    #         title=ft.Text("Add New User"),
    #         content=ft.Column([username_field, password_field, level_field, role_dropdown]),
    #         actions=[ft.TextButton("Add", on_click=submit_new_user)],
    #     )
    #     page.dialog.open = True
    #     page.update()

    def create_rows():
        return [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(user[1]), color="white")),  # UserID
                    ft.DataCell(ft.Text(user[2], color="white")),  # Name
                    ft.DataCell(ft.Text(user[3] if password_visible else "******", color="white")),  # Password
                    ft.DataCell(ft.Text(str(user[4]), color="white")),  # Level
                    ft.DataCell(ft.Text(user[5], color="white")),  # Role
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    on_click=lambda e, user_id=user[0]: edit_role_dialog(user_id),
                                    icon_color="yellow"
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    on_click=lambda e, user_id=user[0]: delete_user_action(user_id),
                                    icon_color="red"
                                ),
                            ]
                        )
                    )
                ]
            ) for user in users
        ]

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("UserID", size=20, weight=ft.FontWeight.BOLD, color="white")),
            ft.DataColumn(ft.Text("Name", size=20, weight=ft.FontWeight.BOLD, color="white")),
            ft.DataColumn(ft.Text("Password", size=20, weight=ft.FontWeight.BOLD, color="white")),
            ft.DataColumn(ft.Text("Level", size=20, weight=ft.FontWeight.BOLD, color="white")),
            ft.DataColumn(ft.Text("Role", size=20, weight=ft.FontWeight.BOLD, color="white")),
            ft.DataColumn(ft.Text("Actions", size=20, weight=ft.FontWeight.BOLD, color="white")),
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

    back_button = ft.ElevatedButton("Back to Main Page", on_click=lambda e: page.go("/edit_page"))

    add_user_button = ft.ElevatedButton("Add New User", on_click=lambda e: page.go("/add_new_user"))

    return ft.View(
        "/account_management",
        [
            ft.AppBar(
                title=ft.Text("Account Management", color="white"),
                bgcolor="#222222",
                actions=[
                    ft.TextButton("Account Management", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/account_management")),
                    ft.TextButton("Quiz Management", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/edit_page")),
                    ft.TextButton("Profile", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/profile_management")),
                    ft.TextButton("Logout", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/")),
                ],
            ),
            ft.Row([toggle_button, table], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([add_user_button], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([back_button], alignment=ft.MainAxisAlignment.CENTER),
        ],
        bgcolor="#343434"
    )