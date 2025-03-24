import pygame
from database import Retrieve_Question, select_user
import time

pygame.init()


def wrap_text_word_based(text, max_width, font):
    """
    Word-wraps the given text so that each line's pixel width (using the provided font)
    does not exceed max_width. If a word would make the line too long, it is moved to the next line.
    Returns the wrapped lines and a boolean indicating if all lines have been completed.
    """
    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        if current_line == "":
            test_line = word
        else:
            test_line = current_line + " " + word

        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line == "":
                lines.append(word)
                current_line = ""
            else:
                lines.append(current_line)
                current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def streak(user_answer):
    number = [0, 0]
    for i in user_answer:
        if i:
            number[0] += 1
        else:
            if number[0] > number[1]:
                number[1] = number[0]
            number[0] = 0
    if number[0] > number[1]:
        return number[0]
    return number[1]


def result(chapter_info, user_answer, resource_path, return_menu, player_info):
    def Arrow(direction, position, color="blue", push=""):
        if push == "":
            path = resource_path(f"assets/MV_Icons_Letter_Buttons/Buttons/{color}-!arrow{direction}{push}.png")
        else:
            path = resource_path(f"assets/MV_Icons_Letter_Buttons/Buttons/{color}-!arrow{direction}-{push}.png")
        arrows = pygame.image.load(path)
        arrows = pygame.transform.scale(arrows, (32 * 2, 32 * 2))
        return [arrows, arrows.get_rect(topleft=position)]

    running = True
    font = pygame.font.Font(resource_path("assets/PeaberryBase.ttf"), 20)
    sec_font = pygame.font.Font(resource_path("assets/PeaberryBase.ttf"), 30)
    third_font = pygame.font.Font(resource_path("assets/PeaberryBase.ttf"), 40)
    screen = pygame.display.set_mode((1280, 800), pygame.FULLSCREEN)
    proceed_text = sec_font.render("PROCEED", True, (255, 255, 255))
    scale = 2
    proceed_button = pygame.Rect(427.15 * scale, 247 * scale, 99 * scale, 38 * scale)

    list_of_answer = []
    for index, i in enumerate(Retrieve_Question(chapter_info[0], "CorrectAnswer")):
        if i == "A":
            list_of_answer.append(Retrieve_Question(chapter_info[0], "Option1")[index])
        elif i == "B":
            list_of_answer.append(Retrieve_Question(chapter_info[0], "Option2")[index])
        elif i == "C":
            list_of_answer.append(Retrieve_Question(chapter_info[0], "Option3")[index])
        elif i == "D":
            list_of_answer.append(Retrieve_Question(chapter_info[0], "Option4")[index])
    list_of_questions = Retrieve_Question(chapter_info[0], "Question")
    questions = len(list_of_questions)
    questions_per_page = 5
    current_page = 0
    total_pages = (questions + questions_per_page - 1) // questions_per_page
    Streak = third_font.render(f"x{streak(user_answer)} Combo", True, (255, 255, 255))
    displayed_text = [""] * questions
    char_index = [0] * questions
    display_answer = [""] * len(list_of_answer)
    char_index_answer = [0] * len(list_of_answer)
    clock = pygame.time.Clock()
    Push_r = ""
    Push_l = ""
    while running:
        screen.fill((52, 52, 52))
        right = Arrow("right", (588, 710), push=Push_r)
        left = Arrow("left", (75, 710), push=Push_l)

        # Calculate current page indices and arrow visibility
        start_idx = current_page * questions_per_page
        end_idx = min(start_idx + questions_per_page, questions)
        show_left = current_page > 0
        show_right = current_page < total_pages - 1
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if show_right and right[1].collidepoint(event.pos):
                    current_page += 1
                    Push_r = "pushed"
                elif show_left and left[1].collidepoint(event.pos):
                    current_page -= 1
                    Push_l = "pushed"
                elif proceed_button.collidepoint(event.pos):
                    print("Result proceed...")
                    return_menu(select_user(player_info[0]))

            elif event.type == pygame.MOUSEBUTTONUP:
                if right[1].collidepoint(event.pos):
                    Push_r = ""
                elif left[1].collidepoint(event.pos):
                    Push_l = ""
        pygame.draw.rect(screen, (39, 70, 68), (100, 40, 526, 698), border_radius=7)
        for i in range(start_idx, end_idx):
            position_in_page = i - start_idx

            if char_index[i] < len(list_of_questions[i]):
                char_index[i] += 1
                displayed_text[i] = list_of_questions[i][:char_index[i]]

                display_answer[i] = list_of_answer[i][:char_index_answer[i]]
            # Animate letter-by-letter for each answer
            if char_index_answer[i] < len(list_of_answer[i]):
                char_index_answer[i] += 1
                display_answer[i] = list_of_answer[i][:char_index_answer[i]]

            wrapped_lines = wrap_text_word_based(displayed_text[i], 370, font)
            base_y_offset = 70
            answer_wrap = wrap_text_word_based(display_answer[i], 370, font)

            # Render the question
            for j, line in enumerate(wrapped_lines):
                # Only the first line gets the question number prefix.
                if j == 0:
                    line_to_render = f"{i + 1}. {line}"
                else:
                    line_to_render = line
                text_surface = font.render(line_to_render, True, (255, 255, 255))
                # Each wrapped line beyond the first gets an extra y-offset of 30 pixels.
                screen.blit(text_surface, (150, base_y_offset + (position_in_page * 137.7) + (j * 30)))

            # Calculate the y-offset for the answer based on the number of lines in the question
            answer_y_offset = base_y_offset + (position_in_page * 137.7) + (len(wrapped_lines) * 30)

            # Render the answer
            for j, line in enumerate(answer_wrap):
                if user_answer[i]:
                    text_surface = font.render(line, True, (0, 204, 100))
                else:
                    text_surface = font.render(line, True, (255, 0, 0))

                # Each wrapped line beyond the first gets an extra y-offset of 20 pixels.
                screen.blit(text_surface, (150, answer_y_offset + (j * 20)))
            if show_right:
                screen.blit(right[0], (588, 710))
            if show_left:
                screen.blit(left[0], (75, 710))

        screen.blit(Streak, (960, 246))
        pygame.draw.rect(screen, (24, 33, 199), (427.15 * scale, 247 * scale, 99 * scale, 38 * scale)
                         , border_radius=8)
        screen.blit(proceed_text, (444 * scale, 260 * scale))
        pygame.display.update()
        time.sleep(0.02)
        clock.tick(60)

    pygame.quit()

