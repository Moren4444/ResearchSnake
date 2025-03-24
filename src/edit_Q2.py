import os
import sys

import flet as ft
from database import (Retrieve_Question, Chapter_Quiz, Update_Question, Delete_Question, Add_Question, Add_QuizLVL,
                      Delete_QuizLVL, Delete_All, Update_title, Add_ChapterDB, Delete_Chapter, Update_Database)
import json


def main(page: ft.Page):
    try:
        page.title = "Edit Question"

        def load_login_credentials():
            """Load credentials from the JSON file."""
            if os.path.exists("Quiz_draft.json"):
                with open("Quiz_draft.json", "r") as file:
                    return json.load(file)
            # return {"username": "", "password": ""}  # Return empty values if file doesn't exist

        def save_login_credentials(chapter_key, quiz_index, info, update=None,
                                   question=""):
            """Save hashed credentials to a JSON file."""
            if update is None:
                update = ['A', 'Option 1', 'Option 2', 'Option 3', 'Option 4']
            if info == 4:
                chapter[chapter_key][quiz_index][info][question] = update
            else:
                chapter[chapter_key][quiz_index][info] = update
            with open("Quiz_draft.json", "w") as file:
                json.dump(chapter, file, indent=4)

        def rename_question_key(chapter_key, quiz_index, old_question, new_question):
            """Rename a question key while keeping its original order."""

            rename = chapter[str(chapter_key)][quiz_index][4]  # Access questions dictionary

            if old_question in rename:
                new_questions = {}

                # Rebuild the dictionary with the new key in the same position
                for key, value in rename.items():
                    if key == old_question:
                        new_questions[new_question] = value  # Insert new key with old value
                    else:
                        new_questions[key] = value  # Keep other questions unchanged

                chapter[str(chapter_key)][quiz_index][4] = new_questions  # Update JSON data

                with open("Quiz_draft.json", "w") as file:
                    json.dump(chapter, file, indent=4)

        def add_new_quiz(chapter_key, new_quiz_data):
            """Add a new quiz to the specified chapter."""

            # Ensure chapter_key exists and is a list
            chapter.setdefault(chapter_key, [])

            # Append the new quiz at the next available index
            chapter[chapter_key].append(new_quiz_data)

            # Save back to file
            with open("Quiz_draft.json", "w") as file:
                json.dump(chapter, file, indent=4)

        def delete_last_quiz(chapter_key):
            """Delete the last quiz in the given chapter key."""

            # Check if the chapter_key exists and has quizzes
            if chapter_key in chapter and isinstance(chapter[chapter_key], list) and chapter[chapter_key]:
                chapter[chapter_key].pop()  # Remove the last quiz

                # Save updated data
                with open("Quiz_draft.json", "w") as file:
                    json.dump(chapter, file, indent=4)
                print(f"Last quiz in chapter '{chapter_key}' has been deleted.")
            else:
                print(f"No quizzes found in chapter '{chapter_key}'.")

        def add_new_chapter_with_quiz():
            chapter[str(len(chapter) + 1)] = [[
                "Quiz Name",
                "Description",
                1,
                str(len(chapter) + 1),
                {"Question 1": [
                    "A",
                    "Option 1",
                    "Option 2",
                    "Option 3",
                    "Option 4"
                ]}
            ]]
            with open("Quiz_draft.json", "w") as file:
                json.dump(chapter, file, indent=4)

        def delete_last_question(chapter_key="1"):
            """Delete the last question from the specified chapter key in the JSON file."""

            # Ensure the key exists in the data
            if chapter_key in chapter:
                quizzes = chapter[chapter_key]  # Access the quizzes list under the chapter key

                if quizzes:  # Ensure there is at least one quiz
                    last_quiz = quizzes[0]  # Assuming we modify the first quiz set
                    questions_dict = last_quiz[4]  # The dictionary containing questions

                    if questions_dict:  # Ensure questions exist
                        last_question = list(questions_dict.keys())[-1]  # Get the last question key
                        print(f"Deleting: {last_question}")

                        # Remove the last question
                        del questions_dict[last_question]

                        # Save the updated JSON back to the file
                        with open("Quiz_draft.json", "w") as file:
                            json.dump(chapter, file, indent=4)

                        print(f"Deleted '{last_question}' from chapter {chapter_key}.")

        def delete_last_chapter():
            """Delete the last numeric key from the JSON data."""

            if not chapter:
                print("No data found in the JSON file.")
                return

            # Find the last key (highest number)
            last_key = max(map(int, chapter.keys()), default=None)  # Convert keys to int, find max

            if last_key is not None:
                last_key_str = str(last_key)  # Convert back to string
                del chapter[last_key_str]  # Remove the last key

                # Save the updated data
                with open("Quiz_draft.json", "w") as file:
                    json.dump(chapter, file, indent=4)

                print(f"Chapter '{last_key_str}' has been deleted.")
            else:
                print("No chapters found to delete.")

        # Database setup
        chapter = load_login_credentials()
        question_store = []
        option_store = []
        answer_store = []
        selected_chapter_index = 1
        Questions = [question_store.append(i) for i in chapter[str(selected_chapter_index)][0][4]]
        Options = [option_store.append(i[1:]) for i in chapter["1"][0][4].values()]
        Answer = [answer_store.append(i[0]) for i in chapter["1"][0][4].values()]
        # Add unsaved changes tracking
        unsaved_changes = False
        pending_question = None
        pending_index = 0

        # Populate chapter_quizzes dictionary

        # Create options for the dropdown
        options_list = []
        for i in range(len(chapter["1"])):
            options_list.append(f"Quiz {i + 1}")
        # Widgets
        default_value = options_list[0] if options_list else None
        original_data = {}
        current_q_index = 0  # Track current question's position
        selected_index = options_list.index(default_value) if default_value else 0  # Global index

        dd = ft.Dropdown(
            border_color="#FFFFFF",
            width=200,
            value=default_value,
            text_style=ft.TextStyle(
                weight=ft.FontWeight.BOLD,
                size=16,
                color="#FFFFFF"
            ),
            options=[ft.dropdown.Option(opt) for opt in options_list],
            bgcolor="#000000",
            border_radius=5,
        )

        quiz_name = ft.TextField(
            border_color="#FFFFFF",
            width=337,
            bgcolor="#496158",
            text_style=ft.TextStyle(
                weight=ft.FontWeight.BOLD,
                size=20,
                color="#FFFFFF"
            ),
            border_radius=5
        )
        description = ft.TextField(
            border_color="#FFFFFF",
            width=540,
            bgcolor="#496158",
            text_style=ft.TextStyle(
                weight=ft.FontWeight.BOLD,
                size=20,
                color="#FFFFFF"
            ),
            border_radius=5,
            multiline=True,
            min_lines=3,  # Minimum visible lines
            max_lines=3,  # Maximum visible lines before scrolling
            expand=True,  # Expands to fill available space
        )

        # Left side components
        cl = ft.Column(
            spacing=20,
            height=350,
            width=314,
            scroll=ft.ScrollMode.ALWAYS,
        )

        # Right side form components
        question_title = ft.TextField(
            label="Question",
            width=400,
            border_color="#FFFFFF",
            min_lines=3,
            max_lines=3,
            text_style=ft.TextStyle(color="#FFFFFF")
        )

        # Modify the option_fields creation to include click handlers
        option_fields = [
            ft.TextField(
                width=200,
                border_color="#FFFFFF",
                text_style=ft.TextStyle(color="#FFFFFF"),
                on_focus=lambda e, idx=i: option_clicked(e, idx),
                bgcolor=ft.colors.RED
            ) for i in range(4)
        ]
        question_title.value = question_store[0]
        answer = answer_store[0]
        options = option_store[0]
        for i in range(4):
            option_fields[i].value = options[i]
            option_fields[i].bgcolor = ft.colors.GREEN if i == (ord(answer) - ord('A')) else ft.colors.RED

        print("See: ", option_store)
        Quiz_name = chapter["1"][0][0]
        lvl_req = chapter["1"][0][2]

        def add_question(e):
            # Add_Question(selected_index + 1)
            index = len(chapter["1"][0][4])
            while f"Question {index}" in chapter[str(selected_chapter_index)][selected_index][4]:
                index += 1
            save_login_credentials(str(selected_chapter_index), selected_index, 4,
                                   question=f"Question {index}")
            update_column(selected_index)

            question_title.value = questions[0]
            options = ["Option 1", "Option 2", "Option 3", "Option 4"]
            answer = "A"
            for i in range(4):
                print(options[i])
                option_fields[i].value = options[i]
                option_fields[i].bgcolor = ft.colors.GREEN if i == (ord(answer) - ord('A')) else ft.colors.RED
                option_fields[i].disabled = False
            question_title.disabled = False
            quiz_name.disabled = False
            description.disabled = False

        def handle_close(e):
            nonlocal unsaved_changes
            page.close(dlg_modal)
            page.update()

        # Add this function to handle option clicks
        def option_clicked(e, index):
            # Reset all options to red
            for opt in option_fields:
                opt.bgcolor = ft.colors.RED
            # Set clicked option to green
            e.control.bgcolor = ft.colors.GREEN
            page.update()

        def update_record(e):
            nonlocal unsaved_changes, original_data
            current_question = question_title.value
            current_options = [field.value for field in option_fields]

            # Find which option is green (correct answer)
            correct_index = next((i for i, opt in enumerate(option_fields) if opt.bgcolor == ft.colors.GREEN), 0)
            correct_answer = chr(65 + correct_index)  # Convert to A-D
            # question_database = Retrieve_Question(selected_index + 1, "Question")[current_q_index]
            # question_json = chapter[str(selected_chapter_index)][selected_index]

            check = questions[:]
            check.pop(current_q_index)
            print("Check: ", check)

            if current_question not in check:
                # Update the database
                question = questions[current_q_index]

                # save_login_credentials(selected_chapter_index, selected_index, 4, question=str(question),
                #                        update=question_title.value)
                new_options = [
                    correct_answer,
                    current_options[0],
                    current_options[1],
                    current_options[2],
                    current_options[3]
                ]
                print(current_q_index)
                print("Check check: ", selected_index, type(selected_index))
                print("Question: ", question, " / ", question_title.value)
                save_login_credentials(str(selected_chapter_index), selected_index, 4, new_options, question)
                print(chapter[str(selected_chapter_index)][selected_index][4])
                if question != question_title.value:
                    rename_question_key(str(selected_chapter_index), selected_index, question, question_title.value)

                save_login_credentials(str(selected_chapter_index), selected_index, 0, update=quiz_name.value)
                save_login_credentials(str(selected_chapter_index), selected_index, 1, update=description.value)

                # Reset unsaved changes flag
                unsaved_changes = False
                # Show a success snackbar
                page.snack_bar = ft.SnackBar(
                    ft.Text("Changes saved!", color="#FFFFFF", weight=ft.FontWeight.BOLD),
                    bgcolor="#242323",
                    duration=1000
                )
                page.snack_bar.open = True
                page.open(page.snack_bar)

                # Close the dialog
                # handle_close(e)

                # Refresh the left container to reflect the updated question
                print("Testing: ", chapter[str(selected_chapter_index)][selected_index][4])
                update_column(selected_index)
                page.update()

            # Load the pending question if there is one
            if pending_question:
                load_question(pending_question)

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Unsaved changed"),
            content=ft.Text("Do you want to save?"),
            actions=[
                ft.TextButton("Yes", on_click=lambda e: (update_record(e), handle_close(e))),
                ft.TextButton("No", on_click=lambda e: discard_changes(e)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def discard_changes(e):
            nonlocal unsaved_changes, pending_question
            unsaved_changes = False
            dlg_modal.open = False
            page.update()
            if pending_question:
                load_question(pending_question)

        def load_question(question):
            nonlocal pending_question
            pending_question = None
            update_question_details(question, selected_index)

        # Modified question tap handler
        def handle_question_tap(q):
            nonlocal unsaved_changes, pending_question
            if unsaved_changes:
                pending_question = q
                dlg_modal.open = True
                page.open(dlg_modal)
                page.update()
            else:
                update_question_details(q, selected_index)

            # Add change detection to input fields

        def mark_unsaved(e):
            nonlocal unsaved_changes
            unsaved_changes = True

        for field in [question_title] + option_fields:
            field.on_change = mark_unsaved

        save_button = ft.ElevatedButton(
            text="Save",
            bgcolor="#4CAF50",
            color="#FFFFFF",
            width=150,
            height=40,
            on_click=update_record,
        )

        # for i in Retrieve_Question()

        # Right side layout
        right_column = ft.Column(
            [
                ft.Text("Question", size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                question_title,
                ft.Row([option_fields[0], option_fields[1]], spacing=20),
                ft.Row([option_fields[2], option_fields[3]], spacing=20),
            ],
            spacing=20,
            width=500,
            height=330
        )
        questions = []

        def update_questions():
            """Updates question_store with the latest questions."""
            questions.clear()  # Clear previous questions
            option_store.clear()  # Ensure old options are removed
            answer_store.clear()  # Ensure old answers are removed
            questions_dict = chapter.get(str(selected_chapter_index), [[]])[selected_index][4]
            questions.extend(questions_dict.keys())  # Append new questions
            option_store.extend([Option[1:] for Option in questions_dict.values()])
            answer_store.extend(questions_dict.values())

        update_questions()
        for i in questions:
            cl.controls.append(
                ft.GestureDetector(
                    content=ft.Container(
                        content=ft.Text(
                            f"{i}",
                            size=16,
                            color=ft.colors.WHITE
                        ),
                        padding=10,
                        border=ft.border.all(1, "#FFFFFF"),
                        border_radius=5,
                        width=280
                    ),
                    on_tap=lambda e, q=i: handle_question_tap(q),
                    on_secondary_tap=lambda e, q=i: delete_question(q)  # Right-click handler
                )
            )

        def save_record(e, index, question):
            current_question = question_title.value
            current_options = [field.value for field in option_fields]
            if original_data.get("options") is not None:
                db_options = [str(opt[0]) if isinstance(opt, tuple) else str(opt) for opt in
                              original_data.get("options")]
                if current_question != original_data.get("question") or current_options != db_options:
                    page.open(dlg_modal)

        # Function to handle question deletion
        def delete_question(question):
            # Confirm deletion with a dialog
            confirm_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirm Delete"),
                content=ft.Text(f"Are you sure you want to delete this question?"),
                actions=[
                    ft.TextButton("Yes", on_click=lambda e: confirm_delete(question)),
                    ft.TextButton("No", on_click=lambda e: close_delete_dialog(e)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            # Open the confirmation dialog
            page.dialog = confirm_dialog
            page.open(page.dialog)
            page.update()

        # Function to confirm deletion
        def confirm_delete(question):
            # Perform the deletion logic here
            quiz_id = selected_index + 1
            question_index = questions.index(question) + 1
            # Call a function to delete the question from the database
            # Delete_Question(quiz_id, question)  # You need to implement this function in your database module
            print(questions, selected_index, selected_chapter_index)
            if selected_chapter_index == 1 and selected_index == 0 and len(questions) == 1:
                warning = ft.AlertDialog(title=ft.Text("Cannot delete the last question"))
                page.open(warning)
                return
            delete_last_question(str(selected_chapter_index))
            # Close the dialog
            close_delete_dialog(None)

            # Refresh the questions list
            update_column(selected_index)
            if not questions or current_q_index == len(questions):
                question_title.disabled = True
                quiz_name.disabled = True
                description.disabled = True
                for i in range(4):
                    option_fields[i].disabled = True
            page.update()

        # Function to close the delete confirmation dialog
        def close_delete_dialog(e):
            page.dialog.open = False
            page.update()

        # Function to update questions list
        def update_column(selected_idx):
            nonlocal selected_index, unsaved_changes
            questions.clear()
            if unsaved_changes:
                dlg_modal.open = True
                page.open(dlg_modal)
                page.update()
            else:
                selected_index = selected_idx
                cl.controls.clear()
                update_questions()
                print(selected_index, selected_chapter_index)
                print("Updating: ", questions)
                for i in questions:
                    cl.controls.append(
                        ft.GestureDetector(
                            content=ft.Container(
                                content=ft.Text(
                                    f"{i}",
                                    size=16,
                                    color=ft.colors.WHITE
                                ),
                                padding=10,
                                border=ft.border.all(1, "#FFFFFF"),
                                border_radius=5,
                                width=280
                            ),
                            on_tap=lambda e, q=i: handle_question_tap(q),
                            on_secondary_tap=lambda e, q=i: delete_question(q)  # Right-click handler
                        )
                    )
                cl.update()

        # Function to update right panel with question details
        def update_question_details(question, index):
            nonlocal current_q_index, original_data
            update_questions()
            current_q_index = questions.index(question)
            print("Index: ", selected_index, selected_chapter_index)
            print(option_store)
            # Get original data from database
            original_question = questions[current_q_index]
            original_options = option_store[current_q_index]
            original_answer = answer_store[current_q_index][0]

            # Store original values
            original_data = {
                "question": original_question,
                "options": original_options,
                "answer": original_answer
            }

            # Update UI fields
            question_title.value = original_question
            question_title.disabled = False
            quiz_name.disabled = False
            description.disabled = False
            print("What is this: ", original_options)
            for i in range(4):
                option_fields[i].value = original_options[i]
                option_fields[i].bgcolor = ft.colors.GREEN if i == (ord(original_answer) - ord('A')) else ft.colors.RED
                option_fields[i].disabled = False
            page.update()

        quiz_name.value = chapter[str(selected_chapter_index)][0][0]
        description.value = chapter[str(selected_chapter_index)][0][1]

        # Dropdown change handler
        def dropdown_changed(e):
            nonlocal selected_index, selected_chapter_index
            selected_index = options_list.index(dd.value)
            selected_chapter_index = int(chapter_dd.value[-1])
            update_questions()

            selected_index = int(chapter[str(selected_chapter_index)][selected_index][2]) - 1
            quiz_name.value = chapter[str(selected_chapter_index)][selected_index][0]
            description.value = chapter[str(selected_chapter_index)][selected_index][1]
            print("Check the index: ", selected_index)
            options_list.clear()
            for i in range(len(chapter[str(selected_chapter_index)])):
                options_list.append(f"Quiz {i + 1}")

            if dd.value not in options_list:
                dd.value = "Quiz 1"
            dd.options = [ft.dropdown.Option(opt) for opt in options_list]

            if questions:
                options = option_store[0]
                answer = answer_store[current_q_index][0]
                question_title.value = questions[0]
                print("Answer: ", answer)
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
            update_column(selected_index)
            page.update()

        dd.on_change = dropdown_changed

        mode_list = [
            (ft.icons.REMOVE_RED_EYE_ROUNDED, "View"),  # Tuple (icon, label)
            (ft.icons.EDIT, "Edit")
        ]
        mode = ft.Dropdown(
            border_color="#FFFFFF",
            width=70,
            value=mode_list[1][1],
            height=45,
            options=[
                ft.dropdown.Option(
                    text=label,
                    content=ft.Row([
                        ft.Icon(icon, size=28),  # ✅ Display icon
                    ])
                ) for icon, label in mode_list
            ],
            bgcolor="#000000"
        )

        def Add_Quiz(e):
            lvl = len(chapter[str(selected_chapter_index)]) + 1
            # new_quiz = (str(get_id), "Quiz Name", "Description", lvl, selected_chapter_index, 1)
            new_quiz = [
                "Quiz Name",
                "Description",
                lvl,
                str(selected_chapter_index),
                {}
            ]
            add_new_quiz(str(selected_chapter_index), new_quiz)
            options_list.clear()
            for i in range(len(chapter[str(selected_chapter_index)])):
                options_list.append(f"Quiz {i + 1}")
            dd.options = [ft.dropdown.Option(opt) for opt in options_list]

            dd.update()

        def confirm_delete_quiz(e):
            # Delete_All(quiz_id)
            # Delete_QuizLVL(chapter_quizzes[len(chapter_quizzes)][-1][0])
            delete_last_quiz(selected_chapter_index)
            page.open(delete_snack)
            options_list.clear()
            for i in range(len(chapter[str(selected_chapter_index)])):
                options_list.append(f"Quiz {i + 1}")
            dd.options = [ft.dropdown.Option(opt) for opt in options_list]
            dd.value = "Quiz 1"
            dd.update()
            page.close(delete_quiz)

            update_column(chapter[str(selected_chapter_index)][0][2])

        def Delete_Quiz(e):
            nonlocal option_store, answer_store
            if len(chapter[str(selected_chapter_index)]) == 1:
                dlg = ft.AlertDialog(
                    title=ft.Text("Minimum 1 quiz!"),
                    on_dismiss=lambda e: page.add(ft.Text("Non-modal dialog dismissed")),
                )
                page.open(dlg)
            else:
                if load_login_credentials()[str(selected_chapter_index)][selected_index][4]:
                    page.open(delete_quiz)
                else:
                    delete_last_quiz(str(selected_chapter_index))
                    options_list.clear()

                    for i in range(len(chapter[str(selected_chapter_index)])):
                        options_list.append(f"Quiz {i + 1}")
                    dd.options = [ft.dropdown.Option(opt) for opt in options_list]
                    dd.value = "Quiz 1"
                    quiz_name.value = chapter[str(selected_chapter_index)][0][0]
                    description.value = chapter[str(selected_chapter_index)][0][1]
                    update_column(chapter[str(selected_chapter_index)][0][2] - 1)
                    dd.update()
                    question_title.value = questions[0]
                    options = option_store[current_q_index]
                    answer = answer_store[current_q_index][0]
                    question_title.disabled = False
                    quiz_name.disabled = False
                    description.disabled = False
                    for i in range(4):
                        option_fields[i].value = options[i]
                        option_fields[i].bgcolor = ft.colors.GREEN if i == (ord(answer) - ord('A')) else ft.colors.RED
                        option_fields[i].disabled = False
                    page.update()

                    page.open(delete_snack)

        delete_snack = ft.SnackBar(
            ft.Text(f"'{Quiz_name}' in Quiz {lvl_req} is deleted!", color="#FFFFFF", weight=ft.FontWeight.BOLD),
            bgcolor="#242323",
            duration=1500
        )

        delete_quiz = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"There's questions inside Quiz {lvl_req}, are you sure you wanna delete?"),
            actions=[
                ft.TextButton("Yes", on_click=lambda e: confirm_delete_quiz(e)),
                ft.TextButton("No", on_click=lambda e: page.close(delete_quiz)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        pb = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(text="Add", on_click=Add_Quiz),
                ft.PopupMenuItem(text="Delete", on_click=Delete_Quiz)
            ],
            width=37
        )
        top_row = ft.Row(
            [
                dd,
                pb,
                mode,
            ],
            spacing=16,
            alignment=ft.MainAxisAlignment.START
        )

        chapter_dd = ft.Dropdown(
            options=[ft.dropdown.Option(f"Chapter {i + 1}") for i in range(len(chapter))],
            width=300,
            value=f"Chapter {selected_chapter_index}",
            border_radius=5,
            color="#FFFFFF",
            bgcolor="#000000",
            border_color="#FFFFFF"
        )

        def add_chapter(e):
            print("Selected Index: ", selected_index)
            if len(chapter) >= 9:
                exceed_alert = ft.AlertDialog(title=ft.Text("Cannot exceed more than 9 Chapter"))
                page.open(exceed_alert)
                return
            # chap_id = Add_ChapterDB()

            chapter_snack = ft.SnackBar(ft.Text(f"A new chapter has been added", color="#FFFFFF",
                                                weight=ft.FontWeight.BOLD), duration=1500, bgcolor="#242323")
            # quiz_id = Add_QuizLVL(1, chap_id) + 1
            # chapter_quizzes[chap_id] = [(quiz_id, "Quiz Name", "Description", 1, chap_id, 1)]

            add_new_chapter_with_quiz()
            chapter_dd.options = [ft.dropdown.Option(f"Chapter {i + 1}") for i in range(len(chapter))]
            chapter_dd.update()
            page.open(chapter_snack)

        def confirm_delete_chapter(e):
            nonlocal selected_index, selected_chapter_index
            # print(chapter_quizzes[len(chapter_quizzes)])
            list_quiz_chapter = []
            if len(chapter) == 1:
                warning = ft.AlertDialog(
                    title=ft.Text("Maximum 9 chapter")
                )
                page.open(warning)
                return
            for i in chapter:
                list_quiz_chapter.append(int(i))
            delete_last_chapter()
            chapter_dd.options = [ft.dropdown.Option(f"Chapter {i + 1}") for i in range(len(chapter))]
            print("Chapter: ", chapter_dd.value)
            if chapter_dd.value == f"Chapter {len(chapter) + 1}":
                selected_chapter_index = 1
                update_questions()
                chapter_dd.value = "Chapter 1"
                quiz_name.value = chapter["1"][0][0]
                description.value = chapter["1"][0][1]
                update_column(0)
                question_title.value = questions[0]
                options = option_store
                answer = answer_store[current_q_index][0]
                options_list.clear()
                for i in range(len(chapter[str(selected_chapter_index)])):
                    options_list.append(f"Quiz {i + 1}")
                dd.options = [ft.dropdown.Option(opt) for opt in options_list]

                for i in range(4):
                    option_fields[i].value = options[0][i]
                    option_fields[i].bgcolor = ft.colors.GREEN if i == (ord(answer) - ord('A')) else ft.colors.RED
                page.update()

            chapter_dd.update()
            ft.SnackBar(ft.Text("Chapter has been deleted!", color="#FFFFFF", weight=ft.FontWeight.BOLD),
                        duration=1500, bgcolor="#242323")

        def delete_chapter(e):
            delete_alert = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirm delete?"),
                content=ft.Text("Are you sure you want to delete chapter?"),
                actions=[ft.TextButton("Yes", on_click=lambda e: [confirm_delete_chapter(e), page.close(delete_alert)]),
                         ft.TextButton("No", on_click=lambda e: page.close(delete_alert))],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.open(delete_alert)

        add_chap = ft.FloatingActionButton(icon=ft.Icons.ADD, bgcolor=ft.Colors.LIME_300,
                                           on_click=add_chapter)
        remove_chap = ft.FloatingActionButton(icon=ft.Icons.REMOVE, bgcolor=ft.Colors.RED_500,
                                              on_click=delete_chapter)
        add_ques = ft.FloatingActionButton(icon=ft.Icons.ADD, bgcolor=ft.Colors.LIME_300, on_click=add_question)

        def preset_close(e):
            add_chap.visible = False
            remove_chap.visible = False
            add_ques.visible = False
            publish_button.visible = False
            # save_button.on_click =
            Update_Database()
            page.update()

        closing_preset = ft.AlertDialog(
            modal=True,
            title=ft.Text("Publish"),
            content=ft.Text("When continue this, you have acknowledge that it will no longer add any "
                            "quiz and chapter.\nDo you want to proceed?"),
            actions=[
                ft.TextButton("Yes", on_click=lambda e: [preset_close(e), page.close(closing_preset)]),
                ft.TextButton("No", on_click=lambda e: page.close(closing_preset))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        publish_button = ft.ElevatedButton(
            text="Publish",
            bgcolor="#e8480e",
            color="#FFFFFF",
            width=150,
            height=40,
            on_click=lambda e: page.open(closing_preset),
        )

        bottom_row = ft.Column(
            [ft.Row([publish_button, save_button], alignment=ft.MainAxisAlignment.END)],
            width=540
        )

        # Main layout
        main_row = ft.Row(
            [
                # Left panel
                ft.Column(
                    [
                        quiz_name,
                        top_row,
                        ft.Container(
                            content=cl,
                            border=ft.border.all(1, "#FFFFFF"),
                            border_radius=5,
                            padding=10,
                            bgcolor="#353232",
                        ),
                        add_ques
                    ],
                    width=350
                ),
                ft.Column(
                    [
                        description,
                        # Right panel
                        ft.Container(
                            content=right_column,
                            border=ft.border.all(1, "#FFFFFF"),
                            border_radius=5,
                            padding=20,
                            bgcolor="#353232",
                        ),
                        bottom_row
                    ],
                ),
            ],
            spacing=50,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.START,  # Align columns to the top
        )

        chapter_dd.on_change = dropdown_changed

        chapter_display = ft.Column(
            controls=[
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                chapter_dd,
                                add_chap,
                                remove_chap
                            ],
                            spacing=50
                        ),
                        ft.Divider(color="#FFFFFF", thickness=3),
                    ]
                ),
                main_row
            ],
            width=940,
            spacing=30
        )

        # Add main layout to page
        # page.add(chapter_display)

        # ✅ Call `update_column()` only AFTER the UI is loaded
        def on_view_loaded(e):
            if default_value:
                update_column(options_list.index(default_value))

        page.on_view_populated = on_view_loaded  # Run this after the page is loaded

        return ft.View(
            route="/edit_page",
            controls=[
                ft.AppBar(
                    title=ft.Text("Account Management", color="white"),
                    bgcolor="#222222",
                    actions=[
                        ft.TextButton("Account Management", style=ft.ButtonStyle(color="white"),
                                      on_click=lambda e: page.go("/account_management")),
                        ft.TextButton("Quiz Management", style=ft.ButtonStyle(color="white"),
                                      on_click=lambda e: page.go("/edit_page")),
                        ft.TextButton("Profile", style=ft.ButtonStyle(color="white"),
                                      on_click=lambda e: page.go("/profile_management")),
                        ft.TextButton("Logout", style=ft.ButtonStyle(color="white"), on_click=lambda e: page.go("/")),
                    ],
                ),
                chapter_display
            ],
            bgcolor="#514B4B",
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER

        )
    except KeyError:
        # Add_ChapterDB()
        # Add_QuizLVL(1, 1)
        # Add_Question(1)
        pass


if __name__ == "__main__":
    ft.app(target=main)
