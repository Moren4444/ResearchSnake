import pygame
from database import Chapter_Quiz, Select
from Result import wrap_text_word_based

pygame.init()
running = True
screen = pygame.display.set_mode((1280, 800), pygame.FULLSCREEN)
close = pygame.image.load("assets/close.png")
lock = pygame.image.load("assets/locked.png")
lock_resize = pygame.transform.scale(lock, (140, 140))

close_resize = pygame.transform.scale(close, (30, 30))
close_rect = close_resize.get_rect(topleft=(1200, 55))
scale = 3.193648
testing = {}
list_of_quiz = []
list_of_levels = []
player_level = 3
font = pygame.font.Font("assets/PeaberryBase.ttf", 30)
fonts = pygame.font.Font("assets/PeaberryBase.ttf", 40)
sec_font = pygame.font.Font("assets/PeaberryBase.ttf", 25)

chapter_quizzes = {}
chapter, quiz = Chapter_Quiz()
all_testing_data = {}
length_of_quiz = []  # Now stores (length, y_offset) for each CHAPTER (not quiz)
display_answer = [""]
char_index_answer = [0]
description_title = sec_font.render("Description: ", True, (0, 0, 0))
play = font.render("Play", True, (0, 0, 0))
available_question_quiz = Select("QuizID", "Question")
overlay = pygame.Surface((1280, 800), pygame.SRCALPHA)  # Enable per-pixel alpha
overlay.fill((0, 0, 0, 130))  # RGBA: Black with 100/255 transparency
overlay_rect = overlay.get_rect(topleft=(0, 0))
question_unavailable = sec_font.render("Quiz is not available", True, (255, 255, 255))
print(question_unavailable.get_width())
# Group quizzes by chapter
for i in range(len(quiz)):
    chapter_id = int(quiz[i][4])
    if chapter_id not in chapter_quizzes:
        chapter_quizzes[chapter_id] = []
    chapter_quizzes[chapter_id].append(quiz[i])

# Process each chapter
for chapter_index, (chapter_id, quizzes) in enumerate(chapter_quizzes.items()):
    print(f"Chapter {chapter_id}")

    y_offset = 150 * chapter_index  # +150 y-offset per chapter

    # Calculate length ONCE PER CHAPTER (based on number of quizzes)
    num_quizzes = len(quizzes) - 1
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

while running:
    screen.fill((50, 50, 50))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()  # Get mouse position
            if alert:
                # Close the overlay if clicked anywhere
                if overlay_rect.collidepoint(mouse_pos):
                    alert = False
            else:
                # Handle quiz clicks only when the overlay is not active
                for i, rect in enumerate(list_of_quiz):
                    if rect.collidepoint(mouse_pos):
                        # Check if the quiz is locked
                        if (i + 1) > player_level:
                            alert = True  # Show a "Quiz is locked" message
                            print("Quiz is locked")
                            break  # Skip further processing

                        # Existing logic for available questions
                        print(f"Quiz {i + 1} clicked!")
                        quiz_level = i
                        print(quiz[quiz_level])
                        if int(quiz[quiz_level][0]) <= available_question_quiz:
                            print("Yes")
                            char_index_title = 0
                            char_index_description = 0
                            menu_open = True
                            alert = False
                            break
                        else:
                            menu_open = False
                            alert = True
                if close_rect.collidepoint(mouse_pos):
                    menu_open = False
            # if overlay_rect.collidepoint(event.pos):
            #     alert = False

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

    # Draw ONE background rectangle per chapter
    for length_value, y_offset in length_of_quiz:
        pygame.draw.rect(screen, (105, 105, 105),
                         (40 * scale, 42 * scale + y_offset,  # X, Y
                          length_value, 24 * scale),  # Width, Height
                         border_radius=5
                         )

    # Inside the quiz rendering loop (where quizzes are drawn)
    total_quizzes_rendered = 0
    for keys, value in chapter_quizzes.items():
        y_offset = 150 * (keys - 1)  # +150 y-offset per chapter
        chapter_name = font.render(f"Chapter {keys}", True, (255, 255, 255))
        screen.blit(chapter_name, (100, 100 + y_offset))

        for index, _ in enumerate(value):
            correct_index = total_quizzes_rendered + index
            level = font.render(f"{index + 1}", True, (0, 0, 0))
            pygame.draw.rect(screen, (246, 208, 17), list_of_quiz[correct_index], border_radius=5)
            screen.blit(level, list_of_levels[correct_index])

            # Add lock icon if the quiz is beyond the player's level
            if (correct_index + 1) > player_level:
                lock_rect = lock_resize.get_rect(center=list_of_quiz[correct_index].center)
                screen.blit(lock_resize, lock_rect.topleft)

        total_quizzes_rendered += len(value)

    if alert:
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (100, 100, 100), (480, 350, 320, 100), border_radius=10)
        screen.blit(question_unavailable, (492, 390))

    pygame.display.update()
pygame.quit()
