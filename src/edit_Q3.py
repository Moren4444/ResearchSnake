import asyncio
import os
import random
import sys
import threading

import flet as ft
import pyautogui
import websockets

from database import (Retrieve_Question, Chapter_Quiz, Update_Question, Delete_Question, Add_Question, Add_QuizLVL,
                      Delete_QuizLVL, Delete_All, Update_title, Add_ChapterDB, Delete_Chapter, select)
import json
from admin import AdminPage
H_OFFSET = 8
V_OFFSET = 31
DPI_SCALE = 1.25  # Adjust this according to your display scaling

cursor_containers = {}  # { client_id: ft.Container }
client_colors = {}      # { client_id: str }


def random_color():
    return f"#{random.randint(0, 0xFFFFFF):06x}"


async def websocket_client(page: ft.Page, stack: ft.Stack, get_current_chapter_quiz):
    uri = "ws://localhost:8765"
    my_client_id = None
    current_chapter = 1  # Track locally
    current_quiz = 1  # Track locally
    try:
        async with websockets.connect(uri) as ws:
            async def sender():
                nonlocal current_chapter, current_quiz

                while True:
                    x, y = pyautogui.position()
                    current_chapter, current_quiz = get_current_chapter_quiz()
                    await ws.send(json.dumps({
                        "x": x,
                        "y": y,
                        "chapter": current_chapter,
                        "quiz": current_quiz
                    }))
                    await asyncio.sleep(0.05)

            async def receiver():
                nonlocal my_client_id, current_chapter, current_quiz
                async for message in ws:
                    data = json.loads(message)
                    if data["type"] == "id":
                        my_client_id = data["id"]
                        print(f"My client ID: {my_client_id}")
                    elif data["type"] == "update":
                        data = data["clients"]
                        current_chapter, current_quiz = get_current_chapter_quiz()
                        active_ids = set()

                        for client in data:
                            cid = client["id"]
                            client_chapter = client["chapter"]
                            client_quiz = client["quiz"]
                            # Skip if not in same chapter/quiz
                            if client_chapter != current_chapter or client_quiz != current_quiz:
                                if cid in cursor_containers:
                                    # Remove stale cursor
                                    stack.controls.remove(cursor_containers[cid])
                                    del cursor_containers[cid]
                                    del client_colors[cid]
                                continue
                            if cid == my_client_id:
                                continue  # ❌ Skip own cursor
                            else:
                                x = client["x"]
                                y = client["y"]
                                active_ids.add(cid)

                                if cid not in client_colors:
                                    client_colors[cid] = random_color()

                                if cid not in cursor_containers:
                                    container = ft.Container(
                                        width=50,
                                        height=50,
                                        border_radius=30,
                                        bgcolor=client_colors[cid],
                                        left=0,
                                        top=0,
                                        animate_position=100
                                    )
                                    cursor_containers[cid] = container
                                    stack.controls.append(container)

                                # Update cursor position
                                local_x = (x - H_OFFSET) / DPI_SCALE
                                local_y = (y - V_OFFSET) / DPI_SCALE
                                cursor_containers[cid].left = local_x - 25
                                cursor_containers[cid].top = local_y - 25

                        # ❗️Remove stale cursors
                        for stale_id in list(cursor_containers.keys()):
                            if stale_id not in active_ids:
                                stack.controls.remove(cursor_containers[stale_id])
                                del cursor_containers[stale_id]
                                del client_colors[stale_id]

                    page.update()

            await asyncio.gather(sender(), receiver())

    except Exception as e:
        print(f"WebSocket error: {e}")


def main(page: ft.Page, role, audio1, audio2, admin_Name):
    page.title = "Edit Question"
    page.theme_mode = "dark"
    # Database setup
    chapter, quiz = Chapter_Quiz()
    chapter_quizzes = {}

    # Add unsaved changes tracking
    unsaved_changes = False
    pending_question = None
    Admin = AdminPage(page, role, audio1, audio2, "/edit_page")
    Hedr = Admin.hedrNavFdbkBx

    def load_login_credentials():
        """Load credentials from the JSON file."""
        if os.path.exists("Quiz_draft2.json"):
            with open("Quiz_draft2.json", "r") as file:
                return json.load(file)
        else:
            return {}

    question_saved = load_login_credentials()
    # Populate chapter_quizzes dictionary
    for i in range(len(quiz)):
        chapter_id = int(quiz[i][4][3:])
        if chapter_id not in chapter_quizzes:
            chapter_quizzes[chapter_id] = []
        chapter_quizzes[chapter_id].append(quiz[i])
    # (QuizID, QuizName, Question, lvl, ChapterID, IsDeleted?)
    # Create options for the dropdown
    options_list = []
    for i in range(len(chapter_quizzes[1])):
        options_list.append(f"Quiz {i + 1}")
    # Widgets
    default_value = options_list[0] if options_list else None
    original_data = {}
    current_q_index = 0  # Track current question's position
    selected_chapter_index = 1

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
    selected_index = int(dd.value.split()[-1])

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
    question_title.value = Retrieve_Question(1, "Question")[current_q_index]
    answer = Retrieve_Question(1, "CorrectAnswer")[current_q_index]
    options = Retrieve_Question(1, "Option1, Option2, Option3, Option4")[current_q_index]

    for i in range(4):
        option_fields[i].value = options[i]
        option_fields[i].bgcolor = ft.colors.GREEN if i == (ord(answer) - ord('A')) else ft.colors.RED

    Quiz_name = chapter_quizzes[selected_chapter_index][-1][1]
    lvl_req = chapter_quizzes[selected_chapter_index][-1][3]

    def add_question(e):

        Add_Question(selected_index, admin_Name)
        update_column(selected_index)
        question_title.value = questions[0]
        options = ["Option 1", "Option 2", "Option 3", "Option 4"]
        answer = "A"

        for i in range(4):
            option_fields[i].value = options[i]
            option_fields[i].bgcolor = ft.colors.GREEN if i == (ord(answer) - ord('A')) else ft.colors.RED
            option_fields[i].disabled = False
        question_title.disabled = False
        save_button.disabled = False
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
        question_database = Retrieve_Question(selected_index, "Question")[current_q_index]
        check = questions
        check.pop(current_q_index)
        index = 0
        for i in chapter_quizzes[selected_chapter_index]:
            if int(i[0][3:]) == selected_index:
                if current_question not in check:
                    # Update the database
                    Update_Question(selected_index, question_database,
                                    current_question, current_options,
                                    correct_answer=correct_answer)
                    Update_title([quiz_name.value, description.value], i[3], selected_chapter_index)

                    old_title = chapter_quizzes[selected_chapter_index][index]
                    update_title = (
                        old_title[0], quiz_name.value, description.value, old_title[3], old_title[4])
                    chapter_quizzes[selected_chapter_index].pop(index)
                    chapter_quizzes[selected_chapter_index].insert(0, update_title)

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
                    questions.clear()
                    update_column(selected_index)
                    page.update()
                else:
                    dlg = ft.AlertDialog(
                        title=ft.Text("Duplicated questions detected"),
                        on_dismiss=lambda e: page.add(ft.Text("Non-modal dialog dismissed")),
                    )
                    page.open(dlg)
                    questions.append(current_question)
                    check = questions
            index += 1

        # Load the pending question if there is one
        if pending_question:
            load_question(pending_question)

    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Unsaved changed"),
        content=ft.Text("Do you want to save?"),
        actions=[
            ft.TextButton("Yes", on_click=lambda e: (Json_save(e), handle_close(e))),
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
        update_question_details(question)

    # Modified question tap handler
    def handle_question_tap(q):
        nonlocal unsaved_changes, pending_question
        if unsaved_changes:
            pending_question = q
            dlg_modal.open = True
            page.open(dlg_modal)
            page.update()
        else:
            update_question_details(q)

        # Add change detection to input fields

    def mark_unsaved(e):
        nonlocal unsaved_changes
        unsaved_changes = True

    for field in [question_title] + option_fields:
        field.on_change = mark_unsaved

    def load_login_credentials():
        """Load credentials from the JSON file."""
        if os.path.exists("Quiz_draft2.json"):
            with open("Quiz_draft2.json", "r") as file:
                return json.load(file)
        # return {"username": "", "password": ""}  # Return empty values if file doesn't exist
        return {}

    question_id = select(f"Select * from Question where QuizID = '{f'QIZ{selected_index:02d}'}'")[current_q_index][0]

    def Json_save(e):
        nonlocal unsaved_changes, question_saved
        unsaved_changes = False

        # Ensure JSON structure exists
        chapter_key = str(selected_chapter_index)

        if not os.path.exists("Quiz_draft2.json"):
            question_saved = {}
        else:
            question_saved = load_login_credentials()

        question_saved.setdefault(chapter_key, {})  # Ensure chapter exists

        # Extract quiz number from dd.value
        section_key = dd.value.split()[-1]  # This represents the quiz number
        question_saved[chapter_key].setdefault(section_key, {})
        Answer = "A"
        for i in range(4):
            if option_fields[i].bgcolor == ft.Colors.GREEN:
                Answer = "ABCD"[i]  # Smarter way to determine the answer

        data = [
            question_title.value,
            Answer,
            option_fields[0].value,
            option_fields[1].value,
            option_fields[2].value,
            option_fields[3].value,
            f"{selected_index:02d}"
        ]
        # Add question data
        question_saved[chapter_key][section_key][question_id] = data

        with open("Quiz_draft2.json", "w") as file:
            json.dump(question_saved, file, indent=4)

        json_record = ft.SnackBar(
            ft.Text("Record has been saved in draft!", color="#FFFFFF", weight=ft.FontWeight.BOLD),
            bgcolor="#242323",
            duration=1500
        )
        Admin.hedrNavDraftBtn.disabled = False
        page.update()
        page.open(json_record)

    save_button = ft.ElevatedButton(
        text="Save",
        bgcolor="#4CAF50",
        color="#FFFFFF",
        width=150,
        height=40,
        on_click=Json_save,
    )

    publish_button = ft.ElevatedButton(
        text="Publish",
        bgcolor="#e8480e",
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

    for i in Retrieve_Question(1, "Question"):
        questions.append(i)
        cl.controls.append(
            ft.GestureDetector(
                content=ft.Container(
                    content=ft.Text(
                        f"{i[:45]}..." if len(i) > 45 else f"{i}",
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

    # Function to handle question deletion
    def delete_question(question):
        # Confirm deletion with a dialog
        nonlocal current_q_index
        current_q_index = questions.index(question)
        quiz_id = selected_index
        dlg = ft.AlertDialog(
            title=ft.Text("Minimum 1 Question per Quiz!"),
            on_dismiss=lambda e: page.add(ft.Text("Non-modal dialog dismissed")),
        )
        print(chapter_quizzes[selected_chapter_index][0][0][3:])
        first_quiz = int(chapter_quizzes[selected_chapter_index][0][0][3:])
        if len(Retrieve_Question(first_quiz, "QuizID")) == 1 and int(quiz_id) == first_quiz:
            page.open(dlg)
            return
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
        original_question = Retrieve_Question(quiz_id, "Question")[current_q_index]
        original_options = Retrieve_Question(quiz_id, "Option1, Option2, Option3, Option4")[current_q_index]
        original_answer = Retrieve_Question(quiz_id, "CorrectAnswer")[current_q_index]
        question_title.value = original_question
        for i in range(4):
            option_fields[i].value = original_options[i]
            option_fields[i].bgcolor = ft.colors.GREEN if i == (ord(original_answer) - ord('A')) else ft.colors.RED
        # Open the confirmation dialog
        page.dialog = confirm_dialog
        page.open(page.dialog)
        page.update()

    # Function to confirm deletion
    def confirm_delete(question):
        # Perform the deletion logic here
        nonlocal question_id
        question_id = select(f"Select * from Question where IsDeleted = 0 and"
                             f" QuizID = '{f'QIZ{selected_index:02d}'}'")[current_q_index][
            0]
        quiz_id = selected_index
        # Call a function to delete the question from the database
        Delete_Question(quiz_id, question_id, [str(selected_chapter_index), dd.value.split()[
            -1]])  # You need to implement this function in your database module

        # Close the dialog
        close_delete_dialog(None)

        # Refresh the questions list
        update_column(selected_index)
        # if not questions or current_q_index == len(questions):

        question_title.disabled = True
        save_button.disabled = True
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
            for i in Retrieve_Question(selected_idx, "Question"):
                questions.append(i)
                cl.controls.append(
                    ft.GestureDetector(
                        content=ft.Container(
                            content=ft.Text(
                                f"{i[:45]}..." if len(i) > 45 else f"{i}",
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
    def update_question_details(question):
        nonlocal current_q_index, original_data, question_id
        current_q_index = questions.index(question)
        question_id = select(f"Select * from Question where QuizID = '{f'QIZ{selected_index:02d}'}'")[current_q_index][
            0]
        # Get original data from database
        quiz_id = selected_index
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
        question_title.value = original_question
        question_title.disabled = False
        save_button.disabled = False
        quiz_name.disabled = False
        description.disabled = False
        for i in range(4):
            option_fields[i].value = original_options[i]
            option_fields[i].bgcolor = ft.colors.GREEN if i == (ord(original_answer) - ord('A')) else ft.colors.RED
            option_fields[i].disabled = False
        page.update()

    for i in chapter_quizzes[selected_index]:
        if int(i[3]) == selected_index:
            quiz_name.value = i[1]
            description.value = i[2]

    # Dropdown change handler
    def dropdown_changed(e):
        nonlocal selected_index, selected_chapter_index, current_q_index, question_id
        for cid in list(cursor_containers.keys()):
            stack.controls.remove(cursor_containers[cid])
            del cursor_containers[cid]
            del client_colors[cid]
        selected_chapter_index = int(chapter_dd.value.split()[-1])
        options_list.clear()
        for i in range(len(chapter_quizzes[selected_chapter_index])):
            options_list.append(f"Quiz {i + 1}")
        if dd.value not in options_list:
            dd.value = "Quiz 1"
        selected_index = int(dd.value.split()[-1])
        if selected_chapter_index == 10:
            pb.visible = True
            top_row.spacing = 16
        elif len(chapter_quizzes) > 9 >= selected_chapter_index:
            pb.visible = False
            top_row.spacing = 68
        current_q_index = 0
        print(chapter_quizzes)
        for i in chapter_quizzes[selected_chapter_index]:
            if int(i[3]) == selected_index and int(i[4][3:]) == selected_chapter_index:
                quiz_name.value = i[1]
                description.value = i[2]
                selected_index = int(i[0][3:])
                break  # Exit after finding the first match
        dd.options = [ft.dropdown.Option(opt) for opt in options_list]
        update_column(selected_index)
        if questions:
            options = Retrieve_Question(selected_index, "Option1, Option2, Option3, Option4")[0]
            answer = Retrieve_Question(selected_index, "CorrectAnswer")[0]
            question_title.value = questions[0]
            for i in range(4):
                option_fields[i].value = options[i]
                option_fields[i].bgcolor = ft.colors.GREEN if i == (ord(answer) - ord('A')) else ft.colors.RED
                option_fields[i].disabled = False
            question_title.disabled = False
            save_button.disabled = False
            quiz_name.disabled = False
            description.disabled = False
        else:
            question_title.disabled = True
            quiz_name.disabled = True
            save_button.disabled = True
            description.disabled = True
            for i in range(4):
                option_fields[i].disabled = True
        try:
            question_id = \
                select(f"Select * from Question where QuizID = '{f'QIZ{selected_index:02d}'}'")[current_q_index][0]
        except IndexError:
            pass
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
        lvl = len(chapter_quizzes[selected_chapter_index]) + 1
        get_id = Add_QuizLVL(lvl, f"CHA{selected_chapter_index:02d}")
        new_quiz = (get_id, "Quiz Name", "Description", lvl, f"CHA{selected_chapter_index:02d}")
        chapter_quizzes[selected_chapter_index].append(new_quiz)

        options_list.clear()
        for i in range(len(chapter_quizzes[selected_chapter_index])):
            options_list.append(f"Quiz {i + 1}")
        dd.options = [ft.dropdown.Option(opt) for opt in options_list]

        dd.update()

    def confirm_delete_quiz(e):
        Delete_All(chapter_quizzes[selected_chapter_index][-1][0][3:])

        Delete_QuizLVL(chapter_quizzes[selected_chapter_index][-1][0][3:])
        chapter_quizzes[selected_chapter_index].pop(-1)
        options_list.clear()
        for i in range(len(chapter_quizzes[selected_chapter_index])):
            options_list.append(f"Quiz {i + 1}")
        dd.options = [ft.dropdown.Option(opt) for opt in options_list]
        dd.value = "Quiz 1"
        dd.update()
        try:
            if len(question_saved[str(selected_chapter_index)]) == 1:
                os.remove("Quiz_draft2.json")
            else:
                question_saved[str(selected_chapter_index)].popitem()
                with open("Quiz_draft2.json", "w") as file:
                    json.dump(question_saved, file)
        except Exception as e:
            print(e)
        update_column(int(chapter_quizzes[selected_chapter_index][0][0][3:]))

    def Delete_Quiz(e):
        nonlocal Quiz_name, lvl_req, selected_chapter_index
        print("Chapter Index: ", selected_chapter_index)
        print(chapter_quizzes[selected_chapter_index])
        Quiz_name = chapter_quizzes[selected_chapter_index][-1][1]
        lvl_req = chapter_quizzes[selected_chapter_index][-1][3]
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
                ft.TextButton("Yes", on_click=lambda e: [confirm_delete_quiz(e), page.open(delete_snack),
                                                         page.close(delete_quiz)]),
                ft.TextButton("No", on_click=lambda e: page.close(delete_quiz)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        if len(chapter_quizzes[selected_chapter_index]) == 1:
            dlg = ft.AlertDialog(
                title=ft.Text("Minimum 1 quiz!"),
                on_dismiss=lambda e: page.add(ft.Text("Non-modal dialog dismissed")),
            )
            page.open(dlg)
        else:
            if Delete_QuizLVL(chapter_quizzes[selected_chapter_index][-1][0][3:]):
                page.open(delete_quiz)
            else:
                chapter_quizzes[selected_chapter_index].pop(-1)
                options_list.clear()

                for i in range(len(chapter_quizzes[selected_chapter_index])):
                    options_list.append(f"Quiz {i + 1}")
                dd.options = [ft.dropdown.Option(opt) for opt in options_list]
                dd.value = "Quiz 1"
                quiz_name.value = chapter_quizzes[selected_chapter_index][0][1]
                description.value = chapter_quizzes[selected_chapter_index][0][2]
                print("TesT: ", int(chapter_quizzes[selected_chapter_index][0][0][3:]))
                print(chapter_quizzes[selected_chapter_index][0])
                update_column(int(chapter_quizzes[selected_chapter_index][0][0][3:]))
                dd.update()
                question_title.value = questions[0]
                print(selected_index)
                options = Retrieve_Question(selected_index + 1, "Option1, Option2, Option3, Option4")[0]
                answer = Retrieve_Question(selected_index + 1, "CorrectAnswer")[0]
                question_title.disabled = False
                save_button.disabled = False
                quiz_name.disabled = False
                description.disabled = False
                for i in range(4):
                    option_fields[i].value = options[i]
                    option_fields[i].bgcolor = ft.colors.GREEN if i == (ord(answer) - ord('A')) else ft.colors.RED
                    option_fields[i].disabled = False
                page.update()
                try:
                    if len(question_saved[str(selected_chapter_index)]) == 1:
                        os.remove("Quiz_draft2.json")
                    else:
                        question_saved[str(selected_chapter_index)].popitem()
                        with open("Quiz_draft2.json", "w") as file:
                            json.dump(question_saved, file)
                except Exception as e:
                    print(e)
                page.open(delete_snack)

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
                    ft.FloatingActionButton(icon=ft.Icons.ADD, bgcolor=ft.Colors.LIME_300, on_click=add_question)
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

    chapter_dd = ft.Dropdown(
        options=[ft.dropdown.Option(f"Chapter {i + 1}") for i in range(len(chapter_quizzes))],
        width=300,
        value=f"Chapter {selected_chapter_index}",
        border_radius=5,
        color="#FFFFFF",
        bgcolor="#000000",
        border_color="#FFFFFF"
    )

    def add_chapter(e):
        if len(chapter_quizzes) >= 9:
            exceed_alert = ft.AlertDialog(
                title=ft.Text("Exceeded 9 Chapter"),
                content=ft.Text("Click Yes will permanently remove Add/Remove button, and will proceed for "
                                "Additional"
                                " Quiz"),
                actions=[
                    ft.TextButton("Yes", on_click=lambda e: [update_page(e), page.close(exceed_alert)]),
                    ft.TextButton("No", on_click=lambda e: page.close(exceed_alert))]
            )
            page.open(exceed_alert)
            return
        chap_id = Add_ChapterDB()
        chapter_snack = ft.SnackBar(ft.Text(f"A new chapter has been added", color="#FFFFFF",
                                            weight=ft.FontWeight.BOLD), duration=1500, bgcolor="#242323")
        quiz_id = Add_QuizLVL(1, chap_id)
        chapter_quizzes[int(chap_id[3:])] = [(quiz_id, "Quiz Name", "Description", 1, chap_id)]

        chapter_dd.options = [ft.dropdown.Option(f"Chapter {i + 1}") for i in range(len(chapter_quizzes))]
        chapter_dd.update()
        Add_Question(chapter_quizzes[len(chapter_quizzes)][0][0][3:], admin_Name)
        page.open(chapter_snack)

    add_chap = ft.FloatingActionButton(icon=ft.Icons.ADD, bgcolor=ft.Colors.LIME_300,
                                       on_click=add_chapter)

    def confirm_delete_chapter(e):
        nonlocal selected_index, selected_chapter_index
        if len(chapter_quizzes) == 1:
            return
        list_quiz_chapter = []
        for i in chapter_quizzes[len(chapter_quizzes)]:
            list_quiz_chapter.append(int(i[0][3:]))
        Delete_Chapter(len(chapter_quizzes), list_quiz_chapter)
        chapter_quizzes.popitem()
        if bool(question_saved):
            if len(question_saved) == 1:
                os.remove("Quiz_draft2.json")
            else:
                question_saved.popitem()
                with open("Quiz_draft2.json", "w") as file:
                    json.dump(question_saved, file)
        chapter_dd.options = [ft.dropdown.Option(f"Chapter {i + 1}") for i in range(len(chapter_quizzes))]
        if chapter_dd.value == f"Chapter {len(chapter_quizzes) + 1}":
            chapter_dd.value = "Chapter 1"
            selected_chapter_index = 1
            selected_index = 1
            quiz_name.value = chapter_quizzes[1][0][1]
            description.value = chapter_quizzes[1][0][2]
            update_column(int(chapter_quizzes[1][0][0][3:]))
            question_title.value = Retrieve_Question(1, "Question")[0]
            options = Retrieve_Question(1, "Option1, Option2, Option3, Option4")[0]
            answer = Retrieve_Question(1, "CorrectAnswer")[0]
            for i in range(4):
                option_fields[i].value = options[i]
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

    remove_chap = ft.FloatingActionButton(icon=ft.Icons.REMOVE, bgcolor=ft.Colors.RED_500,
                                          on_click=delete_chapter)

    if len(chapter_quizzes) > 9:
        add_chap.visible = False
        remove_chap.visible = False
        pb.visible = False
        top_row.spacing = 68

    def update_page(e):
        add_chap.visible = False
        remove_chap.visible = False
        pb.visible = False
        top_row.spacing = 68
        chap_id = Add_ChapterDB()
        quiz_id = Add_QuizLVL(1, chap_id)
        chapter_quizzes[int(chap_id[3:])] = [(quiz_id, "Quiz Name", "Description", 1, chap_id), False]
        chapter_dd.options = [ft.dropdown.Option(f"Chapter {i + 1}") for i in range(len(chapter_quizzes))]
        chapter_dd.update()
        print(chapter_quizzes)
        Add_Question(chapter_quizzes[len(chapter_quizzes)][0][0][3:], admin_Name)
        page.update()

    chapter_dd.on_change = dropdown_changed

    chapter_display = ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    chapter_dd,
                                    add_chap,
                                    remove_chap,
                                ],
                                spacing=50
                            ),
                            ft.Divider(color="#FFFFFF", thickness=3),
                        ]
                    ),
                    main_row
                ],
                width=940,
                spacing=30,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER  # Center everything inside the Row
    )
    stack = ft.Stack([
        Hedr,
        chapter_display,
        # Cursors last (top visual layer)
        *cursor_containers.values()
    ], expand=True)

    def get_current_chapter_quiz():
        """Returns tuple of (current_chapter, current_quiz)"""
        nonlocal chapter_dd, dd
        current_chapter = int(chapter_dd.value.split()[-1])
        current_quiz = int(dd.value.split()[-1])
        return current_chapter, current_quiz

    # Start mouse tracking and websocket client
    threading.Thread(target=lambda: asyncio.run(websocket_client(page, stack, get_current_chapter_quiz)), daemon=True).start()
    return ft.View(
        route="/edit_page",
        controls=[
            stack,
            Admin.page.appbar,
        ],
        bgcolor="#514B4B",
    )


if __name__ == "__main__":
    ft.app(target=main)
