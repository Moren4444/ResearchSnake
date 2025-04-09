import os
import sys
import json
import flet as ft
from database import (Retrieve_Question, Chapter_Quiz, Update_Question, Delete_Question,
                      Add_Question, Add_QuizLVL, Delete_QuizLVL, Delete_All, Update_title,
                      Add_ChapterDB, Delete_Chapter, select)


def load_json():
    """Load credentials from the JSON file."""
    if os.path.exists("Quiz_draft2.json"):
        with open("Quiz_draft2.json", "r") as file:
            return json.load(file)
    else:
        return {}


class QuizEditor:
    def __init__(self, page, audio1, audio2):
        self.page = page
        self.audio1 = audio1
        self.audio2 = audio2
        self.initialize_components()
        self.setup_navigation()
        self.load_initial_data()
        self.questions = []
        self.pending_question = None
        self.draft = ft.TextButton("Draft", style=ft.ButtonStyle(color="white"),
                                   on_click=lambda e: page.go("/draft_page"))

    class DatabaseHandler:
        def __init__(self):
            self.chapter, self.quiz = Chapter_Quiz()
            self.chapter_quizzes = self._organize_chapters()

        def _organize_chapters(self):
            chapters = {}
            for q in self.quiz:
                chapter_id = int(q[4])
                chapters.setdefault(chapter_id, []).append(q)
            return chapters

        def get_questions(self, quiz_id, fields):
            return Retrieve_Question(quiz_id, fields)

    class UIComponents:
        def __init__(self, editor):
            self.editor = editor
            self.create_controls()

        def create_controls(self):
            self.quiz_name = ft.TextField(
                border_color="#FFFFFF", width=337, bgcolor="#496158",
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=20, color="#FFFFFF")
            )

            self.description = ft.TextField(
                border_color="#FFFFFF", width=540, bgcolor="#496158", multiline=True,
                min_lines=3, max_lines=3, expand=True,
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=20, color="#FFFFFF")
            )

            self.question_title = ft.TextField(
                label="Question", width=400, border_color="#FFFFFF",
                min_lines=3, max_lines=3, text_style=ft.TextStyle(color="#FFFFFF")
            )

            self.option_fields = [
                ft.TextField(
                    width=200, border_color="#FFFFFF", text_style=ft.TextStyle(color="#FFFFFF"),
                    on_focus=lambda e, idx=i: self.editor.option_clicked(e, idx)
                ) for i in range(4)
            ]

            self.pb = ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(text="Add", on_click=Add_Quiz),
                    ft.PopupMenuItem(text="Delete", on_click=Delete_Quiz)
                ],
                width=37
            )

    class StateManager:
        def __init__(self):
            self.unsaved_changes = False
            self.current_q_index = 0
            self.selected_chapter_index = 1
            self.selected_index = 0
            self.pending_question = None
            self.options_list = []

    def initialize_components(self):
        self.db = self.DatabaseHandler()
        self.state = self.StateManager()
        self.ui = self.UIComponents(self)

        self.setup_dropdowns()
        self.setup_question_list()
        self.setup_buttons()
        self.setup_dialogs()
        load_json()

    def setup_dropdowns(self):
        # Chapter dropdown setup
        self.chapter_dd = ft.Dropdown(
            options=[ft.dropdown.Option(f"Chapter {i + 1}") for i in range(len(self.db.chapter_quizzes))],
            value=f"Chapter {self.state.selected_chapter_index}",
            width=300, border_radius=5, color="#FFFFFF", bgcolor="#000000", border_color="#FFFFFF",
            on_change=self.dropdown_changed
        )

        # Quiz dropdown setup
        options = [f"Quiz {i + 1}" for i in range(len(self.db.chapter_quizzes[self.state.selected_chapter_index]))]
        self.quiz_dd = ft.Dropdown(
            options=[ft.dropdown.Option(opt) for opt in options],
            value=options[0] if options else None,
            border_color="#FFFFFF", width=200, bgcolor="#000000", border_radius=5,
            on_change=self.quiz_selection_changed
        )

    def setup_question_list(self):
        self.question_list = ft.Column(
            spacing=20, height=350, width=314, scroll=ft.ScrollMode.ALWAYS,
            controls=[self.create_question_item(q) for q in self.db.get_questions(1, "Question")]
        )

    def create_question_item(self, question_text):
        return ft.GestureDetector(
            content=ft.Container(
                content=ft.Text(f"{question_text[:45]}..." if len(question_text) > 45 else question_text,
                                size=16, color=ft.colors.WHITE),
                padding=10, border=ft.border.all(1, "#FFFFFF"), border_radius=5, width=280
            ),
            on_tap=lambda e, q=question_text: self.handle_question_tap(q),
            on_secondary_tap=lambda e, q=question_text: self.delete_question(q)
        )

    def setup_buttons(self):
        self.save_button = ft.ElevatedButton(
            text="Save", bgcolor="#4CAF50", color="#FFFFFF",
            width=150, height=40, on_click=self.save_to_json
        )

        self.publish_button = ft.ElevatedButton(
            text="Publish", bgcolor="#e8480e", color="#FFFFFF",
            width=150, height=40, on_click=self.update_record
        )

    def setup_dialogs(self):
        self.unsaved_dialog = ft.AlertDialog(
            modal=True, title=ft.Text("Unsaved changes"),
            content=ft.Text("Do you want to save?"),
            actions=[
                ft.TextButton("Yes", on_click=lambda e: [self.save_to_json(e), self.page.close(self.unsaved_dialog)]),
                ft.TextButton("No", on_click=self.discard_changes),
            ]
        )

    def setup_navigation(self):
        self.page.appbar = ft.AppBar(
            title=ft.Text("Quiz Editor", color="white"),
            bgcolor="#222222",
            actions=[
                self.draft,
                ft.TextButton("Account Management", style=ft.ButtonStyle(color="white"),
                              on_click=lambda e: self.page.go("/account_management")),
                ft.TextButton("Quiz Management", style=ft.ButtonStyle(color="white"),
                              on_click=lambda e: self.page.go("/edit_page")),
                ft.TextButton("Profile", style=ft.ButtonStyle(color="white"),
                              on_click=lambda e: self.page.go("/profile_management")),
                ft.TextButton("Logout", style=ft.ButtonStyle(color="white"),
                              on_click=self.handle_logout)
            ]
        )

    def load_initial_data(self):
        initial_quiz = self.db.chapter_quizzes[self.state.selected_chapter_index][0]
        self.ui.quiz_name.value = initial_quiz[1]
        self.ui.description.value = initial_quiz[2]
        self.load_question_details(0)

    def load_question_details(self, index):
        question_data = self.db.get_questions(self.state.selected_index + 1, "*")[index]
        self.ui.question_title.value = question_data[1]
        for i in range(4):
            self.ui.option_fields[i].value = question_data[i + 2]
            self.ui.option_fields[i].bgcolor = ft.colors.GREEN if i == (
                    ord(question_data[6]) - ord('A')) else ft.colors.RED

    def option_clicked(self, e, index):
        for opt in self.ui.option_fields:
            opt.bgcolor = ft.colors.RED
        e.control.bgcolor = ft.colors.GREEN
        self.page.update()

    def update_record(self, e):
        current_question = self.ui.question_title.value
        current_options = [field.value for field in self.ui.option_fields]

        # Find which option is green (correct answer)
        correct_index = next((i for i, opt in enumerate(self.ui.option_fields) if opt.bgcolor == ft.colors.GREEN), 0)
        correct_answer = chr(65 + correct_index)  # Convert to A-D
        question_database = Retrieve_Question(self.state.selected_index + 1, "Question")[self.state.current_q_index]
        check = self.questions
        check.pop(self.state.current_q_index)
        print("Check: ", check)
        index = 0
        for i in self.db.chapter_quizzes[self.state.selected_chapter_index]:
            if int(i[0]) == self.state.selected_index + 1:
                if current_question not in check:
                    # Update the database
                    Update_Question(self.state.selected_index + 1, question_database,
                                    current_question, current_options,
                                    correct_answer=correct_answer)
                    Update_title([self.ui.quiz_name.value, self.ui.description.value], i[3],
                                 self.state.selected_chapter_index)

                    old_title = self.db.chapter_quizzes[self.state.selected_chapter_index][index]
                    update_title = (
                        old_title[0], self.ui.quiz_name.value, self.ui.description.value, old_title[3], old_title[4],
                        old_title[5])
                    self.db.chapter_quizzes[self.state.selected_chapter_index].pop(index)
                    self.db.chapter_quizzes[self.state.selected_chapter_index].insert(0, update_title)

                    # Reset unsaved changes flag
                    self.state.unsaved_changes = False

                    # Show a success snackbar
                    self.page.snack_bar = ft.SnackBar(
                        ft.Text("Changes saved!", color="#FFFFFF", weight=ft.FontWeight.BOLD),
                        bgcolor="#242323",
                        duration=1000
                    )
                    self.page.snack_bar.open = True
                    self.page.open(self.page.snack_bar)

                    # Close the dialog
                    # handle_close(e)

                    # Refresh the left container to reflect the updated question
                    self.questions.clear()
                    self.quiz_selection_changed(self.state.selected_index)
                    self.page.update()
            index += 1

        # Load the pending question if there is one
        if self.state.pending_question:
            self.load_question(self.state.pending_question)
        pass

    def save_to_json(self, e):
        self.state.unsaved_changes = False

        # Ensure JSON structure exists
        chapter_key = str(self.state.selected_chapter_index)
        question_id = select(f"Select * from Question"
                             f" where QuizID = {self.state.selected_index + 1}")[self.state.current_q_index][0]

        if not os.path.exists("Quiz_draft2.json"):
            question_saved = {}
        else:
            question_saved = load_json()

        question_saved.setdefault(chapter_key, {})  # Ensure chapter exists

        # Extract quiz number from dd.value
        section_key = self.quiz_dd.value.split()[-1]  # This represents the quiz number
        question_saved[chapter_key].setdefault(section_key, {})
        Answer = "A"
        for i in range(4):
            if self.ui.option_fields[i].bgcolor == ft.Colors.GREEN:
                Answer = "ABCD"[i]  # Smarter way to determine the answer

        data = [
            self.ui.question_title.value,
            Answer,
            self.ui.option_fields[0].value,
            self.ui.option_fields[1].value,
            self.ui.option_fields[2].value,
            self.ui.option_fields[3].value,
            self.state.selected_index + 1
        ]
        # Add question data
        question_saved[chapter_key][section_key][int(question_id)] = data

        with open("Quiz_draft2.json", "w") as file:
            json.dump(question_saved, file, indent=4)

        json_record = ft.SnackBar(
            ft.Text("Record has been saved in the JSON file!", color="#FFFFFF", weight=ft.FontWeight.BOLD),
            bgcolor="#242323",
            duration=1500
        )
        self.draft.disabled = False
        self.page.update()
        self.page.open(json_record)
        pass

    def discard_changes(self, e):
        self.state.unsaved_changes = False
        self.page.open(self.unsaved_dialog)
        self.page.update()
        if self.pending_question:
            self.load_question(self.pending_question)

    def update_column(self, selected_idx):
        """Update the question list column with questions for the selected quiz"""
        self.state.selected_index = selected_idx
        quiz_id = selected_idx + 1
        questions = self.db.get_questions(quiz_id, "Question")

        # Clear existing questions
        self.question_list.controls.clear()

        # Add new questions
        for i, question_text in enumerate(questions):
            self.question_list.controls.append(
                self.create_question_item(question_text))

            # Update the UI
            self.question_list.update()

            # Load first question by default if available
            if questions:
                self.load_question_details(0)
                self.state.current_q_index = 0
            else:
                self.clear_question_fields()

    def clear_question_fields(self):
        """Clear all question editing fields"""
        self.ui.question_title.value = ""
        for field in self.ui.option_fields:
            field.value = ""
            field.bgcolor = ft.colors.RED
        self.page.update()

    def handle_question_tap(self, question):
        # Implementation for question selection
        if self.state.unsaved_changes:
            self.pending_question = question
            self.unsaved_dialog.open = True
            self.page.open(self.unsaved_dialog)
            self.page.update()
        else:
            self.update_question_details(question)
        pass

    def load_question(self, question):
        self.pending_question = None
        self.update_question_details(question)

    def delete_question(self, question):
        # Implementation for question deletion
        pass

    def update_question_details(self, question):
        current_q_index = self.questions.index(question)
        # Get original data from database
        quiz_id = self.state.selected_index + 1
        original_question = Retrieve_Question(quiz_id, "Question")[current_q_index]
        original_options = Retrieve_Question(quiz_id, "Option1, Option2, Option3, Option4")[current_q_index]
        original_answer = Retrieve_Question(quiz_id, "CorrectAnswer")[current_q_index]

        # Store original values
        original_data = {
            "question": original_question,
            "options": original_options,
            "answer": original_answer
        }

        # Update UI fields
        self.ui.question_title.value = original_question
        self.ui.question_title.disabled = False
        self.ui.quiz_name.disabled = False
        self.ui.description.disabled = False
        for i in range(4):
            self.ui.option_fields[i].value = original_options[i]
            self.ui.option_fields[i].bgcolor = ft.colors.GREEN if i == (
                        ord(original_answer) - ord('A')) else ft.colors.RED
            self.ui.option_fields[i].disabled = False
        self.page.update()

    def dropdown_changed(self, e):
        selected_index = self.state.options_list.index(self.quiz_dd.value)
        selected_chapter_index = 10 if int(self.chapter_dd.value[-1]) == 0 else int(self.chapter_dd.value[-1])
        if selected_chapter_index == 10:
            self.ui.pb.visible = True
            top_row.spacing = 16
        elif len(self.db.chapter_quizzes) > 9 >= selected_chapter_index:
            self.ui.pb.visible = False
            top_row.spacing = 68
        current_q_index = 0

        for i in chapter_quizzes[selected_chapter_index]:

            if int(i[3]) == selected_index + 1 and int(i[4]) == selected_chapter_index:
                quiz_name.value = i[1]
                description.value = i[2]
                selected_index = int(i[0]) - 1
                break  # Exit after finding the first match
        options_list.clear()
        for i in range(len(chapter_quizzes[selected_chapter_index])):
            options_list.append(f"Quiz {i + 1}")

        if dd.value not in options_list:
            dd.value = "Quiz 1"
        dd.options = [ft.dropdown.Option(opt) for opt in options_list]

        update_column(selected_index)
        if questions:
            options = Retrieve_Question(selected_index + 1, "Option1, Option2, Option3, Option4")[0]
            answer = Retrieve_Question(selected_index + 1, "CorrectAnswer")[0]
            question_title.value = questions[0]
            for i in range(4):
                option_fields[i].value = options[i]
                option_fields[i].bgcolor = ft.colors.GREEN if i == (ord(answer) - ord('A')) else ft.colors.RED
                option_fields[i].disabled = False
            question_title.disabled = False
            quiz_name.disabled = False
            description.disabled = False
        else:
            question_title.disabled = True
            quiz_name.disabled = True
            description.disabled = True
            for i in range(4):
                option_fields[i].disabled = True

        page.update()
        pass

    def quiz_selection_changed(self, e):
        # Handle quiz selection changes
        pass

    def handle_logout(self, e):
        self.page.overlay.extend([self.audio1, self.audio2])
        self.page.go("/")

    def get_view(self):
        return ft.View(
            route="/edit_page",
            controls=[
                ft.Column([
                    ft.Row([self.chapter_dd, self.quiz_dd], spacing=50),
                    ft.Divider(color="#FFFFFF", thickness=3),
                    ft.Row([
                        ft.Column([
                            self.ui.quiz_name,
                            self.question_list,
                            ft.FloatingActionButton(icon=ft.icons.ADD, bgcolor=ft.colors.LIME_300)
                        ], width=350),
                        ft.Column([
                            self.ui.description,
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Question", size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                    self.ui.question_title,
                                    ft.Row(self.ui.option_fields[:2], spacing=20),
                                    ft.Row(self.ui.option_fields[2:], spacing=20),
                                ]),
                                border=ft.border.all(1, "#FFFFFF"), border_radius=5, padding=20, bgcolor="#353232"
                            ),
                            ft.Row([self.publish_button, self.save_button], alignment=ft.MainAxisAlignment.END)
                        ])
                    ], spacing=50)
                ])
            ],
            bgcolor="#514B4B",
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER
        )


def main(page: ft.Page, audio1, audio2):
    editor = QuizEditor(page, audio1, audio2)
    page.add(editor.get_view())


if __name__ == "__main__":
    ft.app(target=main)
