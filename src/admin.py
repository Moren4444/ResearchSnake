import os
import sys

import flet as ft
from Resouce import resource_path


class AdminPage:
    def __init__(self, page: ft.Page, role, audio1, audio2, route):
        self.page = page
        self.route = route
        self.hedrNavFdbk = ft.Text("", size=12, color=ft.Colors.WHITE)

        self.hedrNavFdbkBx = ft.Container(
            content=self.hedrNavFdbk,
            alignment=ft.alignment.top_right,
        )
        draft_png = resource_path("assets/icons/uHedrNavDraftBtn.png")
        acc_png = resource_path("assets/icons/uHedrNavUsersBtn.png")
        quiz_png = resource_path("assets/icons/uHedrNavQuizBtn.png")
        profile_png = resource_path("assets/icons/uHedrNavProfileBtn.png")
        logout_png = resource_path("assets/icons/uHedrNavLogoutBtn.png")

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
                    self.hedrNavFdbk.value = f"Manage {'Student' if role == 'Admin' else 'Admin'} Account"
                    self.hedrNavFdbkBx.margin = ft.margin.only(right=300) if role == "Admin" else ft.margin.only(right=181)
                    self.userBtnPng.src = getColor(self.userBtnPng.src)
                elif e.control.key == "hedrNavQuizBtn":
                    self.hedrNavFdbk.value = "Manage Quiz"
                    self.hedrNavFdbkBx.margin = ft.margin.only(right=221)
                    self.quizBtnPng.src = getColor(self.quizBtnPng.src)
                elif e.control.key == "hedrNavProfileBtn":
                    self.hedrNavFdbk.value = f"Profile"
                    self.hedrNavFdbkBx.margin = ft.margin.only(right=130) if role == "Admin" else ft.margin.only(right=118)
                    self.profileBtnPng.src = getColor(self.profileBtnPng.src)
                elif e.control.key == "hedrNavLogoutBtn":
                    self.hedrNavFdbk.value = f"Logout"
                    self.hedrNavFdbkBx.margin = ft.margin.only(right=25) if role == "Admin" else ft.margin.only(right=13)
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

        def check(e):
            if not os.path.exists("Quiz_draft2.json"):
                alert = ft.AlertDialog(
                    title=ft.Text("Draft not available")
                )
                self.page.open(alert)
                self.page.update()
            else:
                page.go("/draft_page")

        self.hedrNavDraftBtn = ft.ElevatedButton(
            content=self.draftBtnPng,
            key="hedrNavDraftBtn",
            on_hover=hedrOnHover,
            bgcolor="#222222",
            on_click=lambda e: check(e)
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
