import pygame
import time
from database import Retrieve_Question


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


if __name__ == "__main__":

    pygame.init()
    screen = pygame.display.set_mode((1200, 800), pygame.FULLSCREEN)
    paper = pygame.image.load("assets/PNG-Single Sheet.png")
    font = pygame.font.Font("assets/PeaberryBase.ttf", 27)
    paper_s = pygame.transform.scale(paper, (int(paper.get_width() * 1.5), int(paper.get_height() * 1.5)))
    paper_s = pygame.transform.flip(paper_s, True, False)

    # Your questions (replace with your own text if needed)
    list_of_questions = Retrieve_Question(1, "Question")
    list_of_answer = Retrieve_Question(1, "Option1")

    # Variables to store the animated text and track letter progress.
    displayed_text = [""] * len(list_of_questions)
    char_index = [0] * len(list_of_questions)
    display_answer = [""] * len(list_of_answer)
    char_index_answer = [0] * len(list_of_answer)

    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill((50, 50, 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.blit(paper_s, (100, 40))
        base_y_offset = 140
        answer_y = 170

        for i in range(len(list_of_questions)):
            # Animate letter-by-letter for each question
            if char_index[i] < len(list_of_questions[i]):
                char_index[i] += 1
                displayed_text[i] = list_of_questions[i][:char_index[i]]

                display_answer[i] = list_of_answer[i][:char_index_answer[i]]
            # Animate letter-by-letter for each answer
            if char_index_answer[i] < len(list_of_answer[i]):
                char_index_answer[i] += 1
                display_answer[i] = list_of_answer[i][:char_index_answer[i]]

            # Use word-based wrapping so that if a word (like "like") doesn't fully fit,
            # it moves entirely to the next line.
            wrapped_lines = wrap_text_word_based(displayed_text[i], 363, font)

            answer_wrap = wrap_text_word_based(display_answer[i], 363, font)

            # Render the question
            for j, line in enumerate(wrapped_lines):
                # Only the first line gets the question number prefix.
                if j == 0:
                    line_to_render = f"{i + 1}. {line}"
                else:
                    line_to_render = line
                text_surface = font.render(line_to_render, True, (30, 30, 30))
                # Each wrapped line beyond the first gets an extra y-offset of 30 pixels.
                screen.blit(text_surface, (150, base_y_offset + (i * 137.7) + (j * 30)))

            # Calculate the y-offset for the answer based on the number of lines in the question
            answer_y_offset = base_y_offset + (i * 137.7) + (len(wrapped_lines) * 30)

            # Render the answer
            for j, line in enumerate(answer_wrap):
                print(line)
                text_surface = font.render(line, True, (30, 30, 30))
                # Each wrapped line beyond the first gets an extra y-offset of 30 pixels.
                screen.blit(text_surface, (150, answer_y_offset + (j * 30)))

        pygame.display.update()
        time.sleep(0.02)  # Adjust speed of letter animation as needed
        clock.tick(60)

    pygame.quit()
