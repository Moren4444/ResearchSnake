from datetime import datetime, timedelta
import flet as ft
from database import admin_profile_info, stu_profile_info, delete_user
from admin import AdminPage


def account_management(page: ft.Page, role, audio1, audio2):
    if role == "Owner":
        users = admin_profile_info()
    elif role == "Admin":
        users = stu_profile_info()
    Admin = AdminPage(page, role, audio1, audio2, "/account_management")
    Hedr = Admin.hedrNavFdbkBx
    # password_visible = False
    #
    # def toggle_password(e):
    #     nonlocal password_visible
    #     password_visible = not password_visible
    #     table.rows = create_rows()
    #     toggle_button.icon = ft.Icons.REMOVE_RED_EYE if password_visible else ft.Icons.REMOVE_RED_EYE_OUTLINED
    #     page.update()

    def delete_user_action(user_id):
        print(f"Attempting to delete user with ID: {user_id}")

        def confirm_delete(e):
            nonlocal users, role
            # target = "Student" if role == "Admin" else "Admin"
            delete_user(user_id, role)
            users = admin_profile_info() if role == "Owner" else stu_profile_info()
            table.rows = create_rows()
            page.snack_bar = ft.SnackBar(
                content=ft.Text("The user is deleted successfully!", color="white"),
                bgcolor="green"
            )
            page.open(page.snack_bar)
            page.update()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Confirm Deletion"),
            content=ft.Text("Are you sure you want to delete this user?"),
            actions=[
                ft.TextButton("Delete", on_click=lambda e: [confirm_delete(e), page.close(page.dialog)]),
                ft.TextButton("Cancel", on_click=lambda e: page.close(page.dialog)),
            ],
        )
        page.open(page.dialog)
        page.update()

    def time_ago(last_login):
        now = datetime.now()
        diff = now - last_login

        if diff < timedelta(minutes=1):
            return "Just now"
        elif diff < timedelta(hours=1):
            minutes = diff.seconds // 60
            return f"{minutes} min ago"
        elif diff < timedelta(days=1):
            hours = diff.seconds // 3600
            return f"{hours} hour ago" if hours == 1 else f"{hours} hours ago"
        else:
            days = diff.days
            return f"{days} day ago" if days == 1 else f"{days} days ago"

    def create_rows():
        if role == 'Admin':
            return [
                ft.DataRow(
                    cells=[
                        # ft.DataCell(ft.Text(str(user[1]), color="white")),  # UserID
                        ft.DataCell(ft.Text(user[1], color="white")),  # Name
                        ft.DataCell(ft.Text(user[2], color="white")),  # Email Address
                        ft.DataCell(ft.Text(str(user[4]), color="white")),  # Level
                        # ft.DataCell(ft.Text(user[6], color="white")),  # Role
                        ft.DataCell(ft.Text(str(user[5]), color="white")),  # Registered Date
                        ft.DataCell(ft.Text(time_ago(user[-1]), color="white")),  # Last Login
                        ft.DataCell(
                            ft.Row(
                                [
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
        elif role == 'Owner':
            return [
                ft.DataRow(
                    cells=[
                        # ft.DataCell(ft.Text(str(user[1]), color="white")),  # UserID
                        ft.DataCell(ft.Text(user[1], color="white")),  # Name
                        ft.DataCell(ft.Text(user[2], color="white")),  # Email Address
                        # ft.DataCell(ft.Text(user[6], color="white")),  # Role
                        ft.DataCell(ft.Text(str(user[4]), color="white")),  # Registered Date
                        ft.DataCell(ft.Text(time_ago(user[5]), color="white")),  # Last Login
                        ft.DataCell(
                            ft.Row(
                                [
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
            col for col in [
                # ft.DataColumn(ft.Text("UserID", size=20, weight=ft.FontWeight.BOLD, color="white")),
                ft.DataColumn(ft.Text("Name", size=20, weight=ft.FontWeight.BOLD, color="white")),
                ft.DataColumn(ft.Text("Email", size=20, weight=ft.FontWeight.BOLD, color="white")),
                ft.DataColumn(ft.Text("Level", size=20, weight=ft.FontWeight.BOLD, color="white")) if role == "Admin" else None,
                ft.DataColumn(ft.Text("Registered Date", size=20, weight=ft.FontWeight.BOLD, color="white")),
                ft.DataColumn(ft.Text("Last Login", size=20, weight=ft.FontWeight.BOLD, color="white")),
                ft.DataColumn(ft.Text("Actions", size=20, weight=ft.FontWeight.BOLD, color="white")),
            ] if col is not None
        ],
        rows=create_rows(),
        bgcolor="#474747",
        border=ft.border.all(1, "white"),
        heading_row_color="#222222",
        data_row_color={"hovered": "#555555"},
    )

    # toggle_button = ft.IconButton(
    #     icon=ft.Icons.REMOVE_RED_EYE if password_visible else ft.Icons.REMOVE_RED_EYE_OUTLINED,
    #     on_click=toggle_password,
    #     icon_color="white"
    # )

    back_button = ft.ElevatedButton("Logout", on_click=lambda e: page.go("/"))

    add_user_button = ft.ElevatedButton("Add New User", on_click=lambda e: page.go("/add_new_user"))

    return ft.View(
        "/account_management",
        padding=20,
        bgcolor="#343434",
        controls = [
            Admin.page.appbar,
            Hedr,
            ft.Row([table], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([add_user_button], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([back_button], alignment=ft.MainAxisAlignment.CENTER),
        ],
    )
