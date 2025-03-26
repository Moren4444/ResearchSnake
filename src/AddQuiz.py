import flet as ft
from database import Chapter_Quiz
from Result import wrap_text_word_based
import pygame
import sys
import os


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def AddQuiz():
    pygame.init()
    screen = pygame.display.set_mode((1280, 800), pygame.FULLSCREEN)

    scale = 3.193648
    font = pygame.font.Font(resource_path("assets/PeaberryBase.ttf"), 30)
    sec_font = pygame.font.Font(resource_path("assets/PeaberryBase.ttf"), 25)

    quiz_title_field = ft.TextField(
        label="Quiz Title",
        bgcolor="#000000",
        width=156.5 * 3,
        height=25 * 3,
        color="#FFFFFF",
        border_radius=8,
        border_color="#FFFFFF",
    )

    quiz_description_field = ft.TextField(
        label="Quiz Description",
        bgcolor="#000000",
        width=156.5 * 3,
        height=25 * 3,
        color="#FFFFFF",
        border_radius=8,
        border_color="#FFFFFF",
    )

    question_field = ft.TextField(
        label="Question",
        bgcolor="#000000",
        width=156.5 * 3,
        height=25 * 3,
        color="#FFFFFF",
        border_radius=8,
        border_color="#FFFFFF",
    )


AddQuiz()
