import json
import os.path

import flet as ft
from database import select, update_question


def draft_page(page: ft.Page, audio1, audio2):
    page.bgcolor = "#343434"
    if os.path.exists("Quiz_draft2.json"):
        with open("Quiz_draft2.json") as file:
            chapter_quizQ = json.load(file)

    print("Chapter ", sorted(chapter_quizQ)[0])
    print("Quiz ", [sorted(i[-1])[0] for i in chapter_quizQ[sorted(chapter_quizQ)[0]].values()][0])
    cl = ft.Column(
        spacing=25,
        height=500,
        width=700,
        scroll=ft.ScrollMode.ALWAYS
    )

    chapter_dd = ft.Dropdown(
        value=f"Chapter {sorted(chapter_quizQ)[0]}",
        border_radius=5,
        bgcolor="#000000",
        width=200,
        border_color="#FFFFFF",
        options=[ft.dropdown.Option(f"Chapter {i}") for i in sorted(chapter_quizQ)]
    )
    quiz = list(dict.fromkeys(sorted(i[-1])[0] for i in chapter_quizQ[sorted(chapter_quizQ)[0]].values()))
    quiz_dd = ft.Dropdown(
        value=f"Quiz {quiz[0]}",
        border_radius=5,
        bgcolor="#000000",
        width=200,
        border_color="#FFFFFF",
        options=[ft.dropdown.Option(f"Quiz {i}") for i in quiz]
    )
    selected_chapter = f"Chapter {sorted(chapter_quizQ)[0]}".split()[-1]
    selected_quiz = quiz_dd.value[-1] if quiz_dd.value[-1] != "0" else quiz_dd.value[-2:]
    questions = []
    options_map = {"A": 0, "B": 1, "C": 2, "D": 3}

    def delete_draft(e, ID):
        def confirm_delete():
            chapter_quizQ[selected_chapter].pop(str(ID))
            print(chapter_quizQ)
            with open("Quiz_draft2.json", "w") as f:
                json.dump(chapter_quizQ, f, indent=4)
            update_column(selected_quiz)
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

    for index, (questionID, question) in enumerate(chapter_quizQ[selected_chapter].items()):
        if int(selected_quiz) == int(question[-1]):
            option_details = chapter_quizQ[selected_chapter][str(questionID)][2:6]
            answer = option_details[options_map.get(question[1], 3)]
            questions.append(questionID)
            cl.controls.append(
                ft.GestureDetector(
                    content=ft.Container(
                        content=ft.Text(
                            value=f"{question[0]}\nAnswer: {answer}",
                            size=23,
                            color="#FFFFFF"
                        ),
                        padding=10,
                        border_radius=5,
                        border=ft.border.all(1, "#FFFFFF"),
                        width=700
                    ),
                    on_tap=lambda e, q=questionID, i=index: handle_question_tap(q, i),
                    on_double_tap=lambda e, q=questionID: handle_question_double_tap(q),
                    on_secondary_tap=lambda e, q=questionID: delete_draft(e, q),
                )
            )
    # Track the currently inserted edit container (if any)
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
        quest_details = chapter_quizQ[selected_chapter][str(question_id)]
        current_question = quest_details[0]
        Option_details = chapter_quizQ[selected_chapter][str(question_id)][2:6]
        current_answer = chapter_quizQ[selected_chapter][str(question_id)][1]

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
                selected_quiz
            ]
            chapter_quizQ[selected_chapter][str(question_id)] = data
            with open("Quiz_draft2.json", "w") as f:
                json.dump(chapter_quizQ, f, indent=4)
            save_snack = ft.SnackBar(
                ft.Text("Draft has been saved", color="#FFFFFF", weight=ft.FontWeight.BOLD),
                bgcolor="#242323",
                duration=1000
            )

            page.open(save_snack)
            remove_existing_editor()
            update_column(selected_quiz)
            page.update()

        def publish(e):
            Current_question = Edit_question.value
            current_options = [field.value for field in option_fields]

            # Find which option is green (correct answer)
            correct_index = next((i for i, opt in enumerate(option_fields) if opt.bgcolor == ft.colors.GREEN), 0)
            correct_answer = chr(65 + correct_index)  # Convert to A-D
            update_question(f"Update Question set "
                            f"Question = {Current_question}, CorrectAnswer = {correct_answer}, "
                            f"Option1 = {current_options[0]}, Option2 = {current_options[1]}, "
                            f"Option3 = {current_options[2]}, Option4 = {current_options[3]} "
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
        print(idx)
        # Insert the edit_container right after the tapped question (at index idx+1)
        cl.controls.insert(idx + 1, new_edit_container)
        active_edit["index"] = idx
        active_edit["question_id"] = question_id
        page.update()

    def update_column(selected_QZ):
        cl.controls.clear()
        questions.clear()
        remove_existing_editor()
        for Index, (QID, Quest) in enumerate(chapter_quizQ[selected_chapter].items()):
            if int(selected_QZ) == int(Quest[-1]):
                Option_details = chapter_quizQ[selected_chapter][str(QID)][2:6]
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

    def dropdown_change(e):
        nonlocal selected_chapter, selected_quiz, quiz

        selected_chapter = chapter_dd.value.split()[-1]
        chapter_key = selected_chapter.split()[-1]
        quiz = list(dict.fromkeys(sorted(i[-1])[0] for i in chapter_quizQ[chapter_key].values()))
        active_edit["index"] = None
        quiz_dd.options = [ft.dropdown.Option(f"Quiz {i}") for i in sorted(quiz)]
        # quiz_dd.value = f"Quiz {quiz[0]}"
        selected_quiz = quiz_dd.value.split()[-1]
        update_column(selected_quiz)

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
                                  on_click=lambda e: page.go("/stu_account_management")),
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
