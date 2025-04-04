import os
import sys

import flet as ft


class AdminPage:
    def __init__(self, page: ft.Page, role, audio1, audio2, route):
        self.page = page
        self.route = route
        self.hedrNavFdbk = ft.Text("", size=12, color=ft.Colors.WHITE)

        self.hedrNavFdbkBx = ft.Container(
            content=self.hedrNavFdbk,
            padding=0,
            margin=0,
            alignment=ft.alignment.top_right,
        )
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS  # PyInstaller's temp extraction path
        else:
            base_path = os.path.dirname(__file__)  # Normal script execution path

        draft_png = os.path.join(base_path, "assets", "icons", "uHedrNavDraftBtn.png")
        acc_png = os.path.join(base_path, "assets", "icons", "uHedrNavUsersBtn.png")
        quiz_png = os.path.join(base_path, "assets", "icons", "uHedrNavQuizBtn.png")
        profile_png = os.path.join(base_path, "assets", "icons", "uHedrNavProfileBtn.png")
        logout_png = os.path.join(base_path, "assets", "icons", "uHedrNavLogoutBtn.png")

        self.btnWidth = 55
        self.btnHeight = 55
        self.draftBtnPng = ft.Image(
            src=draft_png, width=self.btnWidth, height=self.btnHeight
        )
        self.userBtnPng = ft.Image(
            src=acc_png, width=self.btnWidth, height=self.btnHeight
        )
        self.quizBtnPng = ft.Image(
            src=quiz_png, width=self.btnWidth, height=self.btnHeight
        )
        self.profileBtnPng = ft.Image(
            src=profile_png, width=self.btnWidth, height=self.btnHeight
        )
        self.logoutBtnPng = ft.Image(
            src=logout_png, width=self.btnWidth, height=self.btnHeight
        )

        def getColor(src):
            # Switch from 'uHedr...' to 'cHedr...'
            filename = os.path.basename(src)
            if filename.startswith('u'):
                filename = 'c' + filename[1:]
            return os.path.join(os.path.dirname(src), filename)

        def removerColor(src):
            # Switch from 'cHedr...' to 'uHedr...'
            filename = os.path.basename(src)
            if filename.startswith('c'):
                filename = 'u' + filename[1:]
            return os.path.join(os.path.dirname(src), filename)

        def remainColored(route):
            if route == "/draft_page":
                self.draftBtnPng.src = getColor(self.draftBtnPng.src)
            elif route == "/account_management":
                self.userBtnPng.src = getColor(self.userBtnPng.src)
            elif route == "/edit_page":
                self.quizBtnPng.src = getColor(self.quizBtnPng.src)
            elif route == "/profile_management":
                self.profileBtnPng.src = getColor(self.profileBtnPng.src)

        remainColored(self.route)

        def hedrOnHover(e):
            # function that changes the hedrNavFdbk according to which button is being hovered
            if e.data == "true":
                if e.control.key == "hedrNavDraftBtn":
                    self.hedrNavFdbk.value = f"Drafts"
                    self.hedrNavFdbkBx.margin = ft.margin.only(right=467)
                    self.draftBtnPng.src = getColor(self.draftBtnPng.src)
                elif e.control.key == "hedrNavUsersBtn":
                    self.hedrNavFdbk.value = f"Manage Student Account"
                    self.hedrNavFdbkBx.margin = ft.margin.only(right=300)
                    self.userBtnPng.src = getColor(self.userBtnPng.src)
                elif e.control.key == "hedrNavQuizBtn":
                    self.hedrNavFdbk.value = "Manage Quiz"
                    self.hedrNavFdbkBx.margin = ft.margin.only(right=221)
                    self.quizBtnPng.src = getColor(self.quizBtnPng.src)
                elif e.control.key == "hedrNavProfileBtn":
                    self.hedrNavFdbk.value = f"Profile"
                    self.hedrNavFdbkBx.margin = ft.margin.only(right=130)
                    self.profileBtnPng.src = getColor(self.profileBtnPng.src)
                elif e.control.key == "hedrNavLogoutBtn":
                    self.hedrNavFdbk.value = f"Logout"
                    self.hedrNavFdbkBx.margin = ft.margin.only(right=25)
                    self.logoutBtnPng.src = getColor(self.logoutBtnPng.src)
            else:
                self.hedrNavFdbk.value = ""
                self.draftBtnPng.src = removerColor(self.draftBtnPng.src)
                self.userBtnPng.src = removerColor(self.userBtnPng.src)
                self.quizBtnPng.src = removerColor(self.quizBtnPng.src)
                self.profileBtnPng.src = removerColor(self.profileBtnPng.src)
                self.logoutBtnPng.src = removerColor(self.logoutBtnPng.src)
                remainColored(self.route)
            self.page.update()

        self.hedrNavDraftBtn = ft.ElevatedButton(
            content=self.draftBtnPng,
            key="hedrNavDraftBtn",
            on_hover=hedrOnHover,
            bgcolor="#222222",
            on_click=lambda e: page.go("/draft_page")
        )

        self.hedrNavUsersBtn = ft.ElevatedButton(
            content=self.userBtnPng,
            key="hedrNavUsersBtn",
            on_hover=hedrOnHover,
            bgcolor="#222222",
            on_click=lambda e: page.go("/account_management")
        )

        self.hedrNavQuizBtn = ft.ElevatedButton(
            content=self.quizBtnPng,
            key="hedrNavQuizBtn",
            on_hover=hedrOnHover,
            bgcolor="#222222",
            on_click=lambda e: page.go("/edit_page")
        )

        self.hedrNavProfileBtn = ft.ElevatedButton(
            # One of the buttons in the header navigation bar
            content=self.profileBtnPng,
            key="hedrNavProfileBtn",
            on_hover=hedrOnHover,
            bgcolor="#222222",
            on_click=lambda e: page.go("/profile_management")
        )

        self.hedrNavLogoutBtn = ft.ElevatedButton(
            content=self.logoutBtnPng,
            key="hedrNavLogoutBtn",
            on_hover=hedrOnHover,
            bgcolor="#222222",
            on_click=lambda e: [page.overlay.append(audio1), page.overlay.append(audio2),
                                page.go("/")]
        )
        if not os.path.exists("Quiz_draft2.json"):
            self.hedrNavDraftBtn.disabled = True
        else:
            self.hedrNavDraftBtn.disabled = False

        self.hedrNavBtnsCtner = ft.Container(
            content=ft.Row(
                controls=[
                    *([self.hedrNavDraftBtn] if role == "Admin" else []),
                    self.hedrNavUsersBtn,
                    *([self.hedrNavQuizBtn] if role == "Admin" else []),
                    self.hedrNavProfileBtn,
                    self.hedrNavLogoutBtn
                ],
                spacing=40
            ),
            padding=ft.padding.only(left=10, right=10, top=10, bottom=10),
        )

        self.page.appbar = ft.AppBar(
            bgcolor="#222222",
            title=ft.Text("ResearchSnake", size=32, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
            toolbar_height=90,
            actions=[
                self.hedrNavBtnsCtner
            ],
        )

    def verticalChronologic(self, contents: list):
        contents.append(ft.Container(expand=True))
        contentLayout = ft.Container(
            ft.Column(
                controls=contents
            ),
            padding=ft.padding.only(left=60, right=60, top=10, bottom=60)
        )
        return contentLayout

    def getHedrNav(self):
        return self.hedrNavBtnsCtner
