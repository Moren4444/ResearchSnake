import pygame
from database import Chapter_Quiz, Select, select
from Result_2 import wrap_text_word_based
import sys
import os
from Page_Menu import page_menu
from Resouce import Profile, Keyboard_Writing, RedPanda, Background, resource_path, font


def return_to_menu(player):
    print("Return to menu")
    print(player)
    Menu(player)


def Arrow(direction, position, color="blue", push=""):
    if push == "":
        path = resource_path(f"assets/MV_Icons_Letter_Buttons/Buttons/{color}-!arrow{direction}{push}.png")
    else:
        path = resource_path(f"assets/MV_Icons_Letter_Buttons/Buttons/{color}-!arrow{direction}-{push}.png")
    arrows = pygame.image.load(path)
    arrows = pygame.transform.scale(arrows, (40 * 2, 40 * 2))
    return [arrows, arrows.get_rect(topleft=position)]


def Menu(player_info):
    try:
        global rect
        pygame.init()
        pygame.mixer.init()
        running = True
        screen = pygame.display.set_mode((1280, 800), pygame.FULLSCREEN)
        close = pygame.image.load(resource_path("assets/close.png"))  # Use resource_path
        lock = pygame.image.load(resource_path("assets/locked.png"))  # Use resource_path

        lock_resize = pygame.transform.scale(lock, (140, 140))
        click_path = resource_path("assets/Click_Audio.mp3")
        click_sound = pygame.mixer.Sound(click_path)

        close_resize = pygame.transform.scale(close, (30, 30))
        close_rect = close_resize.get_rect(topleft=(1462, 80))
        scale = 3.9
        player_level = player_info[4]  # Default to 1 if not set
        # background = pygame.image.load(resource_path(f"assets/Background.jpg"))
        # background_scale = pygame.transform.scale(background, (1280, 800))
        background = Background("assets/Menu.gif")
        pygame.mixer.music.load(resource_path("assets/Student_background_audio.mp3"))
        pygame.mixer.music.play(loops=True)
        chapter_quizzes = {}
        chapter, quiz = Chapter_Quiz()
        description_title = font(25).render("Description: ", True, (0, 0, 0))
        play = font(30).render("Play", True, (0, 0, 0))
        play_button = pygame.Rect(1131, 733, 210, 100)

        # available_question_quiz = Select()
        # print("Available", available_question_quiz)
        overlay = pygame.Surface((1600, 1000), pygame.SRCALPHA)  # Enable per-pixel alpha
        overlay.fill((0, 0, 0, 130))  # RGBA: Black with 100/255 transparency
        overlay_rect = overlay.get_rect(topleft=(0, 0))
        question_unavailable = font(25).render("Quiz is not available", True, (255, 255, 255))
        Quit_Text = font(25).render("We will miss you!", True, (255, 255, 255))
        prompt_Text = font(25).render("Are you sure?", True, (255, 255, 255))
        yes_button = font(25).render("YES", True, (255, 255, 255))
        # print(question_unavailable.get_width())
        # Group quizzes by chapter
        panda_spirit = RedPanda(121, 820)
        panda_spirit.reset()

        for i in range(len(quiz)):
            chapter_id = int(quiz[i][4][3:])
            if chapter_id not in chapter_quizzes:
                chapter_quizzes[chapter_id] = []
            chapter_quizzes[chapter_id].append(quiz[i])
        print(chapter_quizzes)
        # Process each chapter
        # for chapter_index, (chapter_id, quizzes) in enumerate(chapter_quizzes.items()):
        #     print(f"Chapter {chapter_id}")
        #
        #     y_offset = 150 * chapter_index  # +150 y-offset per chapter
        #
        #     # Calculate length ONCE PER CHAPTER (based on number of quizzes)
        #     num_quizzes = len(quizzes)
        #     length = (59 * scale) + (25 * num_quizzes * scale)  # Adjust formula as needed
        #
        #     # Store ONE entry per chapter
        #     length_of_quiz.append((length, y_offset))  # Now 1 entry per chapter
        #
        #     # Process quizzes (for rects and levels)
        #     for index, j in enumerate(quizzes):
        #         rect = pygame.Rect(
        #             (53 * scale) + (30 * index * scale),
        #             (45 * scale) + y_offset,
        #             18 * scale,
        #             18 * scale
        #         )
        #         levels = (
        #             (59 * scale) + (30 * index * scale),
        #             (50 * scale) + y_offset
        #         )
        #         list_of_levels.append(levels)
        #         list_of_quiz.append(rect)
        #         all_testing_data[(f"Chapter {chapter_id}", j[0])] = j[1]

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
        home = pygame.image.load(resource_path("assets/Square_Buttons/Home Square Button.png"))
        home_s = pygame.transform.scale(home, (home.get_width() / 3, home.get_height() / 3))
        home_rect = home_s.get_rect(topleft=(1480, 50))
        keyboard = Keyboard_Writing(screen, player_info)
        Logout = False
        Confirm_Logout = False
        confirm_quit = pygame.Rect((screen.get_width() - 380) / 2, (screen.get_height() - 400) / 2, 380, 400)
        while running:
            screen.fill((50, 50, 50))
            # screen.blit(background_scale, (0, 0))
            background.play(screen)
            panda_spirit.draw(screen)
            loc = font(30).render(str(pygame.mouse.get_pos()), True, (255, 255, 255))
            screen.blit(loc, (1100, 0))
            right = Arrow("right", (588, 772), push=Push_r)
            left = Arrow("left", (75, 772), push=Push_l)

            # Calculate current page indices and arrow visibility
            start_idx = current_page * 3
            end_idx = min(start_idx + 3, len(chapter_quizzes))
            show_left = current_page > 0
            show_right = current_page < total_page - 1
            list_of_visible_quizzes = []

            total_quizzes_rendered = 0  # Track global quiz index
            for page_pos, chapter_id in enumerate(sorted_chapters[start_idx:end_idx]):
                y_offset = 182 * page_pos  # Position within current page
                quizzes = chapter_quizzes[chapter_id]

                # Reference
                # self.overlay = pygame.Surface((1280, 800), pygame.SRCALPHA)  # Enable per-pixel alpha
                # self.overlay.fill((0, 0, 0, 130))
                # self.screen.blit(self.overlay, (0, 0))

                # Draw chapter background
                num_quizzes = len(quizzes)
                chap_length = (59 * scale) + (25 * (num_quizzes - 1) * scale)
                shadow = pygame.Surface((chap_length, 24 * scale), pygame.SRCALPHA)
                shadow.fill((0, 0, 0, 130))
                screen.blit(shadow, (37 * scale, 44.5 * scale + y_offset))
                pygame.draw.rect(screen, (217, 99, 30),
                                 (40 * scale, 42 * scale + y_offset,
                                  chap_length, 24 * scale),
                                 border_radius=5)

                # Draw chapter name
                chapter_name = font(30).render(f"{'Additional Chapter' if chapter_id > 9 else f'Chapter {chapter_id}'}",
                                               True, (0, 0, 0))
                screen.blit(chapter_name, (120, 123 + y_offset))

                # Draw quizzes
                for index, quiz_data in enumerate(quizzes):
                    global_idx = [g_idx for (c_id, q, g_idx) in all_quizzes_global
                                  if c_id == chapter_id and q == quiz_data][0]
                    rect = pygame.Rect(
                        (53 * scale) + (30 * index * scale),
                        (45 * scale) + y_offset,
                        19 * scale,
                        18 * scale
                    )
                    level_pos = (
                        (60 * scale) + (30 * index * scale),
                        (51 * scale) + y_offset
                    )
                    list_of_visible_quizzes.append((rect, global_idx))

                    # 🎯 Add hover detection here
                    if rect.collidepoint(pygame.mouse.get_pos()):
                        if (global_idx + 1) > player_level:
                            pygame.draw.rect(screen, (246, 208, 17), rect, border_radius=5)  # Original yellow
                        else:
                            pygame.draw.rect(screen, (255, 150, 0), rect, border_radius=5)  # Orange highlight
                    else:
                        pygame.draw.rect(screen, (246, 208, 17), rect, border_radius=5)  # Original yellow
                    screen.blit(font(30).render(str(index + 1), True, (0, 0, 0)), level_pos)
                    # Lock logic
                    if (global_idx + 1) > player_level and chapter_id <= 9:
                        lock_rect = lock_resize.get_rect(center=rect.center)
                        screen.blit(lock_resize, lock_rect.topleft)

                total_quizzes_rendered += len(quizzes)  # Update global index

            screen.blit(home_s, (1480, 50))
            mouse_pos = pygame.mouse.get_pos()  # Get mouse position

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    alert = True
                    Confirm_Logout = True
                if event.type == pygame.KEYDOWN:
                    keyboard.handle_keydown(event)
                    if event.key == pygame.K_ESCAPE:
                        alert = True
                        Confirm_Logout = True
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click_sound.play()
                    panda_spirit.handle_click(mouse_pos)
                    keyboard.handle_click(mouse_pos)
                    if alert:
                        # Close the overlay if clicked anywhere
                        if overlay_rect.collidepoint(mouse_pos):
                            running = not Logout

                            if confirm_quit.collidepoint(mouse_pos):
                                if Confirm_Logout and pygame.Rect(700, 570, 200, 50).collidepoint(mouse_pos):
                                    Confirm_Logout = False
                                    Logout = True
                            else:
                                alert = False
                                Confirm_Logout = False
                    profile.handle_click(mouse_pos)
                    if show_left and left[1].collidepoint(mouse_pos):
                        current_page = max(0, current_page - 1)
                    elif show_right and right[1].collidepoint(mouse_pos):
                        current_page = min(total_page - 1, current_page + 1)
                    elif (home_rect.collidepoint(mouse_pos) or profile.open_profile[0]) and not menu_open:
                        profile.open_profile[0] = True
                        if profile.change_rect.collidepoint(mouse_pos):
                            keyboard.open_overlay = True
                        elif profile.logout_rect.collidepoint(mouse_pos):
                            alert = True
                            Logout = True
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
                                        print("Yes: ", Select()[quiz_level][1])
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
                        elif play_button.collidepoint(mouse_pos) and menu_open:
                            try:
                                selected_quiz = all_quizzes_global[quiz_level][1]  # (chap_id, q_data, g_idx)
                                page_menu(player_info, selected_quiz, return_to_menu, resource_path, quiz_level + 1,
                                          click_sound)
                                pygame.display.quit()
                                # Run Page-Menu.py and pass quiz[quiz_level] as a command-line argument
                                # subprocess.run([sys.executable, "Page-Menu.py", str(quiz[quiz_level]), str(player_info)])
                                sys.exit()  # Exit the current script
                            except Exception as e:
                                print("HAI: ", e)
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

            if menu_open:
                try:
                    level_click = quiz[quiz_level]

                    pygame.draw.rect(screen, (254, 204, 146), (965, 45, 542, 842))
                    screen.blit(close_resize, (1462, 80))
                    # Animate the title
                    title = level_click[1][:char_index_title]
                    title_wrapped = wrap_text_word_based(title, 340,
                                                         pygame.font.Font(resource_path("assets/PeaberryBase.ttf"), 30))
                    for i, line in enumerate(title_wrapped):
                        title_surface = font(33).render(line, True, (0, 0, 0))
                        screen.blit(title_surface, (1000, 120 + i * 40))

                    # Animate the description
                    description = level_click[2][:char_index_description]
                    description_wrapped = wrap_text_word_based(description, 340,
                                                               pygame.font.Font(resource_path("assets/PeaberryBase.ttf"),
                                                                                30))
                    screen.blit(description_title, (1000, 254))
                    for i, line in enumerate(description_wrapped):
                        description_surface = font(33).render(line, True, (0, 0, 0))
                        screen.blit(description_surface, (1000, 300 + i * 40))  # Adjust y-offset for each line

                    # Update animation progress
                    current_time = pygame.time.get_ticks()
                    if current_time - last_update_time > animation_speed:
                        last_update_time = current_time
                        if char_index_title < len(level_click[1]):
                            char_index_title += 1
                        if char_index_description < len(level_click[2]):
                            char_index_description += 1
                    pygame.draw.rect(screen, (150, 188, 219), play_button, border_radius=5)
                    screen.blit(play, (1131 + (210 - play.get_width())/2, 733 + (100 - play.get_height())/2))
                except Exception as e:
                    print("WHAT: ", e)

            if show_left: screen.blit(left[0], left[1])
            if show_right: screen.blit(right[0], right[1])

            profile.page()
            if keyboard.open_overlay:
                profile.open_profile = [False, False]
                keyboard.page()
                # keyboard.bar_shake(keyboard.input_x + 10 + keyboard.get_x(), keyboard.input_y + 5)

            if alert:
                screen.blit(overlay, (0, 0))
                if Confirm_Logout:
                    pygame.draw.rect(screen, (100, 100, 100), confirm_quit, border_radius=10)
                    screen.blit(prompt_Text, (610 + (380 - prompt_Text.get_width()) / 2, 400))
                    pygame.draw.rect(screen, (0, 131, 96), (700, 570, 200, 50))
                    screen.blit(yes_button, (700 + (200 - yes_button.get_width()) / 2,
                                             570 + (50 - yes_button.get_height()) / 2))

                elif Logout:
                    profile.open_profile = [False, False]
                    pygame.draw.rect(screen, (100, 100, 100), ((screen.get_width() - 480) / 2,
                                                               (screen.get_height() - 200) / 2, 480, 200), border_radius=10)
                    screen.blit(Quit_Text, ((screen.get_width() - Quit_Text.get_width()) / 2,
                                            (screen.get_height() - Quit_Text.get_height()) / 2))
                else:
                    pygame.draw.rect(screen, (100, 100, 100), (480, 350, 320, 100), border_radius=10)
                    screen.blit(question_unavailable, (492, 390))

            pygame.display.update()
    except Exception as e:
        print("Wat: ", e)
    pygame.quit()
