import flet as ft
from database import Retrieve_Question, Chapter_Quiz, Update_Question, Delete_Question


def main(page: ft.Page):
    page.title = "Edit Question"
    page.bgcolor = "#514B4B"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    # Database setup
    chapter, quiz = Chapter_Quiz()
    chapter_quizzes = {}

    # Add unsaved changes tracking
    unsaved_changes = False
    pending_question = None
    pending_index = 0

    # Populate chapter_quizzes dictionary
    for i in range(len(quiz)):
        chapter_id = int(quiz[i][4])
        if chapter_id not in chapter_quizzes:
            chapter_quizzes[chapter_id] = []
        chapter_quizzes[chapter_id].append(quiz[i])

    # Create options for the dropdown
    options_list = []
    for i in range(len(chapter_quizzes[1])):
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
        width=321,
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
    for i in chapter_quizzes[selected_index + 1]:
        if int(i[3]) == selected_index + 1:
            quiz_name.value = i[1]
            description.value = i[2]

    # Left side components
    cl = ft.Column(
        spacing=20,
        height=350,
        width=300,
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

    def add_question(e):
        # Add_Question()
        pass

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
        correct_answer = chr(65 + correct_index) # Convert to A-D

        question_database = Retrieve_Question(selected_index + 1, "Question")[current_q_index]
        check = questions
        check.pop(current_q_index)
        if current_question not in check:
            # Update the database
            Update_Question(selected_index + 1, question_database,
                            current_question, current_options,
                            correct_answer=correct_answer)

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

    def save_record(e, index, question):
        current_question = question_title.value
        current_options = [field.value for field in option_fields]
        if original_data.get("options") is not None:
            db_options = [str(opt[0]) if isinstance(opt, tuple) else str(opt) for opt in original_data.get("options")]
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
        Delete_Question(question_index)  # You need to implement this function in your database module

        # Close the dialog
        close_delete_dialog(None)

        # Refresh the questions list
        questions.clear()
        update_column(selected_index)
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
            for i in Retrieve_Question(selected_idx + 1, "Question"):
                questions.append(i)
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
        current_q_index = questions.index(question)

        # Get original data from database
        quiz_id = selected_index + 1
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
        for i in range(4):
            option_fields[i].value = original_options[i]
            option_fields[i].bgcolor = ft.colors.GREEN if i == (ord(original_answer) - ord('A')) else ft.colors.RED
        page.update()

    # Dropdown change handler
    def dropdown_changed(e):
        nonlocal selected_index
        selected_index = options_list.index(dd.value)
        update_column(selected_index)

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
    top_row = ft.Row(
        [
            dd,
            mode
        ],
        spacing=50,
        alignment=ft.MainAxisAlignment.START
    )
    bottom_row = ft.Column(
        [ft.Row([save_button], alignment=ft.MainAxisAlignment.END)],
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
                    ft.FloatingActionButton(icon=ft.Icons.ADD, bgcolor=ft.Colors.LIME_300)
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

    # Add main layout to page
    page.add(main_row)

    # Initialize with default values
    update_column(options_list.index(default_value))


ft.app(target=main)
