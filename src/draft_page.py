import json
import os.path

import flet as ft
from database import select, update_DB


def draft_page(page: ft.Page, audio1, audio2):
    page.bgcolor = "#343434"
    if os.path.exists("Quiz_draft2.json"):
        with open("Quiz_draft2.json") as file:
            chapter_quizQ = json.load(file)
    sort = sorted(chapter_quizQ)[0]
    selected_chapter = f"Chapter {sort}".split()[-1]

    selected_quiz = f"Quiz {sorted(chapter_quizQ[sort])[int(selected_chapter) - 1]}".split()[-1]
    sorted_chapter = [int(i) for i in sorted(chapter_quizQ)]
    Quiz = chapter_quizQ[str(sorted_chapter[0])]
    sorted_Quiz = [int(i) for i in sorted(Quiz)]
    Question = chapter_quizQ[str(sorted_chapter[0])][str(sorted_Quiz[0])]
    # print("Quiz ", [sorted(i[-1])[0] for i in chapter_quizQ[sorted(chapter_quizQ)[0]].values()][0])
    cl = ft.Column(
        spacing=25,
        height=500,
        width=700,
        scroll=ft.ScrollMode.ALWAYS
    )

    chapter_dd = ft.Dropdown(
        value=f"Chapter {sorted_chapter[0]}",
        border_radius=5,
        bgcolor="#000000",
        width=200,
        border_color="#FFFFFF",
        options=[ft.dropdown.Option(f"Chapter {i}") for i in sorted(chapter_quizQ)]
    )
    quiz = sorted([int(i) for i in chapter_quizQ[str(sorted_chapter[0])]])
    quiz_dd = ft.Dropdown(
        value=f"Quiz {sorted_Quiz[0]}",
        border_radius=5,
        bgcolor="#000000",
        width=200,
        border_color="#FFFFFF",
        options=[ft.dropdown.Option(f"Quiz {i}") for i in quiz]
    )

    questions = []
    options_map = {"A": 0, "B": 1, "C": 2, "D": 3}

    def delete_draft(e, ID):
        def confirm_delete():
            nonlocal selected_quiz, quiz, selected_chapter, Quiz, sorted_Quiz, sorted_chapter
            active_edit["index"] = None
            # Remove the quiz question
            chapter_quizQ[selected_chapter][selected_quiz].pop(str(ID))

            # Remove quiz if empty
            if not chapter_quizQ[selected_chapter][selected_quiz]:
                chapter_quizQ[selected_chapter].pop(selected_quiz)

            # Remove chapter if empty
            if not chapter_quizQ[selected_chapter]:
                chapter_quizQ.pop(selected_chapter)

                # Update chapter selection
                if chapter_quizQ:
                    sorted_chapter = sorted(map(int, chapter_quizQ.keys()))
                    selected_chapter = str(sorted_chapter[0])
                    chapter_dd.value = f"Chapter {selected_chapter}"
                    chapter_dd.options = [ft.dropdown.Option(f"Chapter {ch}") for ch in sorted_chapter]
                else:
                    selected_chapter = None
                    chapter_dd.value = "No Chapters"
                    chapter_dd.options = []

            # Update quiz selection
            if selected_chapter and chapter_quizQ.get(selected_chapter):
                Quiz = chapter_quizQ[selected_chapter]
                sorted_Quiz = sorted(map(int, Quiz.keys()))
                selected_quiz = str(sorted_Quiz[0])
                quiz_dd.value = f"Quiz {selected_quiz}"
                quiz_dd.options = [ft.dropdown.Option(f"Quiz {qz}") for qz in sorted_Quiz]
            else:
                selected_quiz = None
                quiz_dd.value = "No Quizzes"
                quiz_dd.options = []

            # Save updated quiz data
            with open("Quiz_draft2.json", "w") as f:
                json.dump(chapter_quizQ, f, indent=4)

            update_column()
            page.update()

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete this question?"),
            actions=[
                ft.TextButton("Yes", on_click=lambda e: [confirm_delete(), page.close(confirm_dialog)]),
                ft.TextButton("No", on_click=lambda e: page.close(confirm_dialog)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(confirm_dialog)
    active_edit = {"index": None, "question_id": None}

    def remove_existing_editor():
        # Remove the previously inserted edit_container if exists in the column
        if active_edit["index"] is not None:
            # Remove the edit_container from the column controls
            cl.controls.pop(active_edit["index"] + 1)
            active_edit["index"] = None
            active_edit["question_id"] = None

    def handle_question_double_tap(question_id):
        if active_edit["question_id"] == question_id:
            remove_existing_editor()
            page.update()

    def handle_question_tap(question_id, idx):
        if active_edit["question_id"] == question_id:
            return
        remove_existing_editor()  # Remove any editor currently displayed
        # Retrieve current question details
        quest_details = chapter_quizQ[selected_chapter][selected_quiz][str(question_id)]
        current_question = quest_details[0]
        Option_details = quest_details[2:]
        current_answer = quest_details[1]

        # Create editable fields prepopulated with current question and answer
        Edit_question = ft.TextField(
            label="Edit Question",
            value=current_question,
            width=400,
            min_lines=3,
            max_lines=3,
            border_color="#FFFFFF",
            text_style=ft.TextStyle(color="#FFFFFF")
        )
        option_fields = [
            ft.TextField(
                width=190,
                border_color="#FFFFFF",
                text_style=ft.TextStyle(color="#FFFFFF"),
                on_focus=lambda e, Index=i: option_clicked(e, Index),
                bgcolor=ft.colors.RED
            ) for i in range(4)
        ]
        for i in range(4):
            option_fields[i].value = Option_details[i]
            option_fields[i].bgcolor = ft.colors.GREEN if i == (ord(current_answer) - ord('A')) else ft.colors.RED

        def option_clicked(e, INDEX):
            # Reset all options to red
            for opt in option_fields:
                opt.bgcolor = ft.colors.RED
            # Set clicked option to green
            e.control.bgcolor = ft.colors.GREEN
            page.update()

        # Save function – here you can expand to update your data store.
        def save_edit(e):
            Current_question = Edit_question.value
            current_options = [field.value for field in option_fields]

            # Find which option is green (correct answer)
            correct_index = next((i for i, opt in enumerate(option_fields) if opt.bgcolor == ft.colors.GREEN), 0)
            correct_answer = chr(65 + correct_index)  # Convert to A-D
            data = [
                Current_question,
                correct_answer,
                current_options[0],
                current_options[1],
                current_options[2],
                current_options[3],
                chapter_quizQ[selected_chapter][selected_quiz][str(question_id)][-1]
            ]
            chapter_quizQ[selected_chapter][selected_quiz][str(question_id)] = data
            with open("Quiz_draft2.json", "w") as f:
                json.dump(chapter_quizQ, f, indent=4)
            save_snack = ft.SnackBar(
                ft.Text("Draft has been saved", color="#FFFFFF", weight=ft.FontWeight.BOLD),
                bgcolor="#242323",
                duration=1000
            )

            page.open(save_snack)
            remove_existing_editor()
            update_column()
            page.update()

        def publish(e):
            Current_question = Edit_question.value
            current_options = [field.value for field in option_fields]

            # Find which option is green (correct answer)
            correct_index = next((i for i, opt in enumerate(option_fields) if opt.bgcolor == ft.colors.GREEN), 0)
            correct_answer = chr(65 + correct_index)  # Convert to A-D
            quiz_ID = chapter_quizQ[selected_chapter][selected_quiz][str(question_id)][-1]
            check = select(f"Select Question from Question where QuizID = {quiz_ID}")

            if Current_question in [i[0] for i in check]:
                page.open(
                    ft.AlertDialog(
                        title=ft.Text("Question Exist in Database")
                    )
                )
                return
            update_DB(f"Update Question set "
                      f"Question = '{Current_question}', CorrectAnswer = '{correct_answer}', "
                      f"Option1 = '{current_options[0]}', Option2 = '{current_options[1]}', "
                      f"Option3 = '{current_options[2]}', Option4 = '{current_options[3]}' "
                      f"where QuestionID = {question_id}")
            publish_snack = ft.SnackBar(
                ft.Text("Changes saved!", color="#FFFFFF", weight=ft.FontWeight.BOLD),
                bgcolor="#242323",
                duration=1000
            )
            page.open(publish_snack)
            remove_existing_editor()
            page.update()

        save_button = ft.ElevatedButton("Save", bgcolor="#4CAF50",
                                        color="#FFFFFF",
                                        width=150,
                                        height=40,
                                        on_click=save_edit)
        publish = ft.ElevatedButton("Published",
                                    bgcolor="#e8480e",
                                    color="#FFFFFF",
                                    width=150,
                                    height=40,
                                    on_click=publish)

        # Populate the edit_container with these controls
        new_edit_container = ft.Container(
            visible=True,
            content=ft.Column(
                controls=[
                    Edit_question,
                    ft.Row([option_fields[0], option_fields[1]], spacing=20),
                    ft.Row([option_fields[2], option_fields[3]], spacing=20),
                    ft.Row([publish, save_button], spacing=20, alignment=ft.MainAxisAlignment.END),
                ],
                spacing=10,
                width=400
            ),
            margin=ft.margin.only(top=10)
        )
        # Insert the edit_container right after the tapped question (at index idx+1)
        cl.controls.insert(idx + 1, new_edit_container)
        active_edit["index"] = idx
        active_edit["question_id"] = question_id
        page.update()

    def update_column():
        nonlocal sorted_Quiz, Question, sorted_chapter, Quiz
        cl.controls.clear()
        questions.clear()
        remove_existing_editor()
        sorted_chapter = [int(i) for i in sorted(chapter_quizQ)]
        Quiz = chapter_quizQ[str(sorted_chapter[sorted_chapter.index(int(selected_chapter))])]
        sorted_Quiz = [int(i) for i in sorted(Quiz)]
        Question = Quiz[str(sorted_Quiz[sorted_Quiz.index(int(selected_quiz))])]
        for Index, (QID, Quest) in enumerate(Question.items()):
            Option_details = Quest[2:]
            Answer = Option_details[options_map.get(Quest[1], 3)]
            questions.append(QID)
            cl.controls.append(
                ft.GestureDetector(
                    content=ft.Container(
                        content=ft.Text(
                            value=f"{Quest[0]}\nAnswer: {Answer}",
                            size=23,
                            color="#FFFFFF"
                        ),
                        padding=10,
                        border_radius=5,
                        border=ft.border.all(1, "#FFFFFF"),
                        width=700,
                    ),
                    on_tap=lambda e, q=QID, i=Index: handle_question_tap(q, i),
                    on_double_tap=lambda e, q=QID, i=Index: handle_question_double_tap(q),
                    on_secondary_tap=lambda e, q=QID: delete_draft(e, q),
                )
            )
        page.update()  # 🔥 Ensure UI refreshes after changes

    update_column()

    def dropdown_change(e):
        nonlocal selected_chapter, selected_quiz, quiz, sort, sorted_chapter

        selected_chapter = chapter_dd.value.split()[-1]
        sort = sorted(chapter_quizQ[selected_chapter])
        sorted_chapter = [int(i) for i in sorted(chapter_quizQ)]
        temp = quiz
        quiz = sorted([int(i) for i in chapter_quizQ[str(sorted_chapter[sorted_chapter.index(int(selected_chapter))])]])
        active_edit["index"] = None
        if temp != quiz:
            quiz_dd.value = f"Quiz {quiz[0]}"
        page.update()
        quiz_dd.options = [ft.dropdown.Option(f"Quiz {i}") for i in quiz]

        selected_quiz = quiz_dd.value.split()[-1]
        update_column()

    chapter_dd.on_change = dropdown_change
    quiz_dd.on_change = dropdown_change

    top_filer = ft.Row(
        controls=[
            chapter_dd,
            quiz_dd
        ],
        alignment=ft.MainAxisAlignment.START  # Left-align items
    )
    question_details = ft.Column(
        controls=[
            ft.Container(
                content=cl,
                border=ft.border.all(1, "#FFFFFF"),
                border_radius=5,
                padding=10,
                bgcolor="#353232",
            )
        ]
    )
    return ft.View(
        route="/draft_page",
        bgcolor="#343434",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.AppBar(
                title=ft.Text("Account Management", color="white"),
                bgcolor="#222222",
                actions=[
                    ft.TextButton("Draft", style=ft.ButtonStyle(color="white"),
                                  on_click=lambda e: page.go("/draft_page")),
                    ft.TextButton("Account Management", style=ft.ButtonStyle(color="white"),
                                  on_click=lambda e: page.go("/account_management")),
                    ft.TextButton("Quiz Management", style=ft.ButtonStyle(color="white"),
                                  on_click=lambda e: page.go("/edit_page")),
                    ft.TextButton("Profile", style=ft.ButtonStyle(color="white"),
                                  on_click=lambda e: page.go("/profile_management")),
                    ft.TextButton("Logout", style=ft.ButtonStyle(color="white"),
                                  on_click=lambda e: [page.overlay.append(audio1), page.overlay.append(audio2),
                                                      page.go("/")]),
                ],
            ),
            ft.Container(
                content=ft.Column(
                    controls=[top_filer, question_details],  # Add elements inside
                    spacing=15,  # Keep spacing between elements
                    alignment=ft.MainAxisAlignment.CENTER,  # Center vertically inside container
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Center horizontally inside container
                ),
                padding=16,  # Optional padding
                alignment=ft.alignment.center,  # Center the entire container on the page
                width=700,  # 🔥 Add a fixed width to prevent stretching
            )
        ]

    )
