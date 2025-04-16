import pygame
from database import Chapter_Quiz, Select, select
from Result_2 import wrap_text_word_based
import sys
import os
from Page_Menu import page_menu
from Resouce import Profile, Keyboard_Writing


def return_to_menu(player):
    print("Return to menu")
    print(player)
    Menu(player)


def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def Menu(player_info):
    pygame.init()
    pygame.mixer.init()
    running = True
    screen = pygame.display.set_mode((1280, 800), pygame.FULLSCREEN)
    close = pygame.image.load(resource_path("assets/close.png"))  # Use resource_path
    lock = pygame.image.load(resource_path("assets/locked.png"))  # Use resource_path
    lock_resize = pygame.transform.scale(lock, (140, 140))
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS  # PyInstaller's temp extraction path
    else:
        base_path = os.path.dirname(__file__)  # Normal script execution path
    click_path = os.path.join(base_path, "assets", "Click_Audio.mp3")
    click_sound = pygame.mixer.Sound(click_path)

    close_resize = pygame.transform.scale(close, (30, 30))
    close_rect = close_resize.get_rect(topleft=(1200, 55))
    scale = 3.193648
    testing = {}
    list_of_quiz = []
    list_of_levels = []
    player_level = player_info[4]  # Default to 1 if not set
    font = pygame.font.Font(resource_path("assets/PeaberryBase.ttf"), 30)
    fonts = pygame.font.Font(resource_path("assets/PeaberryBase.ttf"), 40)
    sec_font = pygame.font.Font(resource_path("assets/PeaberryBase.ttf"), 25)

    chapter_quizzes = {}
    chapter, quiz = Chapter_Quiz()
    all_testing_data = {}
    length_of_quiz = []  # Now stores (length, y_offset) for each CHAPTER (not quiz)
    display_answer = [""]
    char_index_answer = [0]
    description_title = sec_font.render("Description: ", True, (0, 0, 0))
    play = font.render("Play", True, (0, 0, 0))
    play_button = pygame.Rect(935, 550, 210, 100)

    def Arrow(direction, position, color="blue", push=""):
        if push == "":
            path = resource_path(f"assets/MV_Icons_Letter_Buttons/Buttons/{color}-!arrow{direction}{push}.png")
        else:
            path = resource_path(f"assets/MV_Icons_Letter_Buttons/Buttons/{color}-!arrow{direction}-{push}.png")
        arrows = pygame.image.load(path)
        arrows = pygame.transform.scale(arrows, (32 * 2, 32 * 2))
        return [arrows, arrows.get_rect(topleft=position)]

    # available_question_quiz = Select()
    # print("Available", available_question_quiz)
    overlay = pygame.Surface((1280, 800), pygame.SRCALPHA)  # Enable per-pixel alpha
    overlay.fill((0, 0, 0, 130))  # RGBA: Black with 100/255 transparency
    overlay_rect = overlay.get_rect(topleft=(0, 0))
    question_unavailable = sec_font.render("Quiz is not available", True, (255, 255, 255))
    # print(question_unavailable.get_width())
    # Group quizzes by chapter

    for i in range(len(quiz)):
        chapter_id = int(quiz[i][4][3:])
        if chapter_id not in chapter_quizzes:
            chapter_quizzes[chapter_id] = []
        chapter_quizzes[chapter_id].append(quiz[i])
    print(chapter_quizzes)
    # Process each chapter
    for chapter_index, (chapter_id, quizzes) in enumerate(chapter_quizzes.items()):
        print(f"Chapter {chapter_id}")

        y_offset = 150 * chapter_index  # +150 y-offset per chapter

        # Calculate length ONCE PER CHAPTER (based on number of quizzes)
        num_quizzes = len(quizzes)
        length = (59 * scale) + (25 * num_quizzes * scale)  # Adjust formula as needed

        # Store ONE entry per chapter
        length_of_quiz.append((length, y_offset))  # Now 1 entry per chapter

        # Process quizzes (for rects and levels)
        for index, j in enumerate(quizzes):
            rect = pygame.Rect(
                (53 * scale) + (30 * index * scale),
                (45 * scale) + y_offset,
                18 * scale,
                18 * scale
            )
            levels = (
                (59 * scale) + (30 * index * scale),
                (50 * scale) + y_offset
            )
            list_of_levels.append(levels)
            list_of_quiz.append(rect)
            all_testing_data[(f"Chapter {chapter_id}", j[0])] = j[1]

    print(quiz)
    quiz_level = 0
    # Main loop
    menu_open = False

    # Animation variables
    char_index_title = 0
    char_index_description = 0
    last_update_time = pygame.time.get_ticks()
    animation_speed = 50  # Milliseconds per character
    alert = False
    current_page = 0
    sorted_chapters = sorted(chapter_quizzes.keys())
    all_quizzes_global = []
    global_quiz_id = 0
    for chap_id in sorted_chapters:
        quizzes = chapter_quizzes[chap_id]
        for q in quizzes:
            all_quizzes_global.append((chap_id, q, global_quiz_id))
            global_quiz_id += 1
    total_page = (len(sorted_chapters) + 2) // 3
    Push_r = ""
    Push_l = ""
    profile = Profile(screen, player_info)
    center = (1100, 50)
    radius = 23.28
    # Create a Rect around the circle manually
    circle_rect = pygame.Rect(
        center[0] - radius,
        center[1] - radius,
        radius * 2,
        radius * 2
    )
    open_profile = False
    keyboard = Keyboard_Writing(screen)
    while running:
        screen.fill((50, 50, 50))
        loc = font.render(str(pygame.mouse.get_pos()), True, (255, 255, 255))
        screen.blit(loc, (1100, 0))
        right = Arrow("right", (588, 710), push=Push_r)
        left = Arrow("left", (75, 710), push=Push_l)

        # Calculate current page indices and arrow visibility
        start_idx = current_page * 3
        end_idx = min(start_idx + 3, len(chapter_quizzes))
        show_left = current_page > 0
        show_right = current_page < total_page - 1
        list_of_visible_quizzes = []

        total_quizzes_rendered = 0  # Track global quiz index
        for page_pos, chapter_id in enumerate(sorted_chapters[start_idx:end_idx]):
            y_offset = 150 * page_pos  # Position within current page
            quizzes = chapter_quizzes[chapter_id]

            # Draw chapter background
            num_quizzes = len(quizzes)
            chap_length = (59 * scale) + (25 * (num_quizzes - 1) * scale)
            pygame.draw.rect(screen, (105, 105, 105),
                             (40 * scale, 42 * scale + y_offset,
                              chap_length, 24 * scale),
                             border_radius=5)

            # Draw chapter name
            chapter_name = font.render(f"Chapter {'Additional Chapter' if chapter_id > 9 else chapter_id}",
                                       True, (255, 255, 255))
            screen.blit(chapter_name, (100, 100 + y_offset))

            # Draw quizzes
            for index, quiz_data in enumerate(quizzes):
                global_idx = [g_idx for (c_id, q, g_idx) in all_quizzes_global
                              if c_id == chapter_id and q == quiz_data][0]
                rect = pygame.Rect(
                    (53 * scale) + (30 * index * scale),
                    (45 * scale) + y_offset,
                    18 * scale,
                    18 * scale
                )
                level_pos = (
                    (59 * scale) + (30 * index * scale),
                    (50 * scale) + y_offset
                )
                list_of_visible_quizzes.append((rect, global_idx))

                pygame.draw.rect(screen, (246, 208, 17), rect, border_radius=5)
                screen.blit(font.render(str(index + 1), True, (0, 0, 0)), level_pos)
                # Lock logic
                if (global_idx + 1) > player_level and chapter_id <= 9:
                    lock_rect = lock_resize.get_rect(center=rect.center)
                    screen.blit(lock_resize, lock_rect.topleft)

            total_quizzes_rendered += len(quizzes)  # Update global index

        pygame.draw.circle(screen, (217, 217, 217), center, radius)
        mouse_pos = pygame.mouse.get_pos()  # Get mouse position
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                keyboard.handle_keydown(event)
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click_sound.play()
                keyboard.handle_click(mouse_pos)
                if alert:
                    # Close the overlay if clicked anywhere
                    if overlay_rect.collidepoint(mouse_pos):
                        alert = False
                elif profile.overlay_rect.collidepoint(mouse_pos):
                    profile_box = pygame.Rect(120, 81, 1157 - 120, 738 - 81)
                    if not profile_box.collidepoint(mouse_pos):
                        open_profile = False
                if show_left and left[1].collidepoint(mouse_pos):
                    current_page = max(0, current_page - 1)
                elif show_right and right[1].collidepoint(mouse_pos):
                    current_page = min(total_page - 1, current_page + 1)
                elif circle_rect.collidepoint(mouse_pos) or open_profile:
                    open_profile = True
                    if profile.change_rect.collidepoint(mouse_pos):
                        keyboard.open_overlay = True
                else:
                    # Handle quiz clicks only when the overlay is not active
                    for rect, global_idx in list_of_visible_quizzes:
                        if rect.collidepoint(mouse_pos):
                            chapter_id = [c_id for (c_id, q, g_idx) in all_quizzes_global
                                          if g_idx == global_idx][0]
                            if (global_idx + 1) > player_level and chapter_id <= 9:
                                # alert = True  # Show a "Quiz is locked" message
                                print(f"Quiz {global_idx + 1} is locked")
                                break  # Skip further processing

                            # Existing logic for available questions
                            print(f"Quiz {global_idx + 1} clicked!")
                            quiz_level = global_idx
                            print(quiz_level)
                            try:
                                if select(f"Select QuizID from Question where QuizID = '{Select()[quiz_level][1]}'"):
                                    print("Yes")
                                    char_index_title = 0
                                    char_index_description = 0
                                    menu_open = True
                                    alert = False
                                    break
                                else:
                                    menu_open = False
                                    alert = True
                            except Exception as e:
                                print("Issue: ", e)
                    if close_rect.collidepoint(mouse_pos):
                        menu_open = False
                    elif play_button.collidepoint(mouse_pos):
                        selected_quiz = all_quizzes_global[quiz_level][1]  # (chap_id, q_data, g_idx)
                        page_menu(player_info, selected_quiz, return_to_menu, resource_path, quiz_level + 1,
                                  click_sound)
                        pygame.display.quit()
                        # Run Page-Menu.py and pass quiz[quiz_level] as a command-line argument
                        # subprocess.run([sys.executable, "Page-Menu.py", str(quiz[quiz_level]), str(player_info)])
                        sys.exit()  # Exit the current script
            elif event.type == pygame.MOUSEWHEEL:
                try:
                    if profile.history_rect.collidepoint(mouse_pos):
                        if event.y > 0:  # Scroll up
                            profile.scroll_offset = max(0, profile.scroll_offset - profile.y_offset[0])
                        elif event.y < 0:  # Scroll down
                            profile.scroll_offset = min(profile.max_scroll, profile.scroll_offset + profile.y_offset[0])
                    list_of_visible_quizzes.clear()
                except Exception as e:
                    print("Event: ", e)

        if open_profile:
            try:
                profile._draw()
            except Exception as e:
                print(e)
        if keyboard.open_overlay:
            open_profile = False
            keyboard.page()
            # keyboard.bar_shake(keyboard.input_x + 10 + keyboard.get_x(), keyboard.input_y + 5)

        if menu_open:
            level_click = quiz[quiz_level]
            pygame.draw.rect(screen, (110, 110, 110), (800, 50, 445, 650), border_radius=5)
            screen.blit(close_resize, (1200, 55))
            # Animate the title
            title = level_click[1][:char_index_title]
            title_wrapped = wrap_text_word_based(title, 400, font)
            for line in title_wrapped:
                title_surface = font.render(line, True, (0, 0, 0))
                screen.blit(title_surface, (850, 100))

            # Animate the description
            description = level_click[2][:char_index_description]
            description_wrapped = wrap_text_word_based(description, 400, font)
            screen.blit(description_title, (850, 200))
            for i, line in enumerate(description_wrapped):
                description_surface = font.render(line, True, (0, 0, 0))
                screen.blit(description_surface, (850, 250 + i * 40))  # Adjust y-offset for each line

            # Update animation progress
            current_time = pygame.time.get_ticks()
            if current_time - last_update_time > animation_speed:
                last_update_time = current_time
                if char_index_title < len(level_click[1]):
                    char_index_title += 1
                if char_index_description < len(level_click[2]):
                    char_index_description += 1
            pygame.draw.rect(screen, (150, 188, 219), (935, 550, 210, 100), border_radius=5)
            screen.blit(play, (1000, 590))

        if show_left: screen.blit(left[0], left[1])
        if show_right: screen.blit(right[0], right[1])

        if alert:
            screen.blit(overlay, (0, 0))
            pygame.draw.rect(screen, (100, 100, 100), (480, 350, 320, 100), border_radius=10)
            screen.blit(question_unavailable, (492, 390))

        pygame.display.update()
    pygame.quit()
