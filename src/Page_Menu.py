import pygame
from Result_2 import wrap_text_word_based
import sys
from Game_page import Game_page


def page_menu(player_info, chapter_info, return_to_menu_callback, resource_path, quiz_level, click):
    pygame.init()
    running = True
    screen = pygame.display.set_mode((1280, 800), pygame.FULLSCREEN)
    font = pygame.font.Font(resource_path("assets/PeaberryBase.ttf"), 60)
    small_font = pygame.font.Font(resource_path("assets/PeaberryBase.ttf"), 40)
    smaller_font = pygame.font.Font(resource_path("assets/PeaberryBase.ttf"), 30)
    Easy = font.render("Easy", True, (255, 255, 255))
    Medium = font.render("Medium", True, (255, 255, 255))
    Hard = font.render("Hard", True, (255, 255, 255))
    Start = small_font.render("START", True, (255, 255, 255))

    title_letter_index = 0
    description_letter_index = 0
    # chapter_info = eval(sys.argv[1])
    print(chapter_info)
    Chapter = small_font.render(f"Chapter {chapter_info[0]}", True, (255, 255, 255))

    last_update_time = pygame.time.get_ticks()
    scale = 2.8764

    Easy_rect = pygame.Rect(63 * scale, 169 * scale, 102 * scale, 44 * scale)
    Medium_rect = pygame.Rect(172 * scale, 169 * scale, 102 * scale, 44 * scale)
    Hard_rect = pygame.Rect(281 * scale, 169 * scale, 102 * scale, 44 * scale)

    Start_Button = pygame.Rect(369 * scale, 234 * scale, 60 * scale, 27 * scale)
    Push = ""
    release = False
    selected = ["Easy", 180]

    def arrow(color="blue", push=""):
        try:
            if push == "":
                path = resource_path(f"assets/MV_Icons_Letter_Buttons/Buttons/{color}-!arrowleft{push}.png")
            else:
                path = resource_path(f"assets/MV_Icons_Letter_Buttons/Buttons/{color}-!arrowleft-{push}.png")
            arrows = pygame.image.load(path)
        except Exception as e:
            print(f"Failed to load arrow image: {e}")
            arrows = pygame.Surface((64, 64))  # Fallback surface
            arrows.fill((255, 0, 0))  # Red error indicator
        arrows = pygame.transform.scale(arrows, (32 * 2, 32 * 2))
        return [arrows, arrows.get_rect(topleft=(50, 30))]

    print(running)
    while running:
        screen.fill((50, 50, 50))
        mouse = pygame.mouse.get_pos()
        arrow_sprite, arrow_rect = arrow(push=Push)  # Get arrow image & rect
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                click.play()
                if arrow_rect.collidepoint(event.pos):
                    Push = "pushed"
                if Easy_rect.collidepoint(event.pos):
                    print("Easy")
                    selected = ["Easy", 180]
                elif Medium_rect.collidepoint(event.pos):
                    print("Medium")
                    selected = ["Medium", 150]
                elif Hard_rect.collidepoint(event.pos):
                    print("Hard")
                    selected = ["Hard", 100]
                if Start_Button.collidepoint(event.pos):
                    print("Start button clicked")
                    running = False  # Exit the current Pygame loop
                    print(selected)
                    Game_page(player_info, selected[1], return_to_menu_callback, resource_path,
                              chapter_info, quiz_level, click)
                    pygame.display.quit()  # Close the current Pygame window
                    print("Launching Game_page...")
                    print("Game_page exited")
                    # subprocess.run([sys.executable, "Game-page.py", str(player_info)])
                    sys.exit()

            # Mouse Release
            if event.type == pygame.MOUSEBUTTONUP:
                if arrow_rect.collidepoint(event.pos):  # Release inside arrow
                    Push = ""  # Reset
                    release = True

            # Hover Effect (print only if truly hovering)
        if release and arrow_rect.collidepoint(mouse):
            return_to_menu_callback(player_info)
            pygame.quit()
            # subprocess.run([sys.executable, "Menu.py", str(player_info)])
            sys.exit()
        position = smaller_font.render(str(mouse), True, (255, 255, 255))
        screen.blit(position, (1100, 0))
        screen.blit(arrow(push=Push)[0], (50, 30))

        screen.blit(Chapter, (58 * scale, 30 * scale))
        pygame.draw.rect(screen, (217, 217, 217), (89 * scale, 54 * scale, 268 * scale, 32 * scale))
        pygame.draw.rect(screen, (217, 217, 217), (89 * scale, 94 * scale, 268 * scale, 67 * scale))

        # pygame.draw.rect(screen, (0, 170, 37), (63 * scale, 169 * scale, 102 * scale, 44 * scale))

        titles = chapter_info[1][:title_letter_index]
        title_wrap = wrap_text_word_based(titles,  330 * scale, small_font)

        descriptions = chapter_info[2][:description_letter_index]
        des_wrap = wrap_text_word_based(descriptions, 330 * scale, small_font)
        for index, line in enumerate(title_wrap):
            title_surface = smaller_font.render(line, True, (0, 0, 0))
            screen.blit(title_surface, (93 * scale, (58 * scale) + (index * 35)))

        for index, line in enumerate(des_wrap):
            des_surface = smaller_font.render(line, True, (0, 0, 0))
            screen.blit(des_surface, (93 * scale, (97 * scale) + (index * 35)))
        # difficulties level
        pygame.draw.rect(screen, (0, 170, 37), (63 * scale, 169 * scale, 102 * scale, 44 * scale))
        pygame.draw.rect(screen, (171, 119, 23), (172 * scale, 169 * scale, 102 * scale, 44 * scale))
        pygame.draw.rect(screen, (189, 3, 3), (281 * scale, 169 * scale, 102 * scale, 44 * scale))

        if selected[0] == "Easy":
            pygame.draw.rect(screen, (0, 0, 0), (63 * scale, 169 * scale, 102 * scale, 44 * scale), width=5)
        elif selected[0] == "Medium":
            pygame.draw.rect(screen, (0, 0, 0), (172 * scale, 169 * scale, 102 * scale, 44 * scale), width=5)
        elif selected[0] == "Hard":
            pygame.draw.rect(screen, (0, 0, 0), (281 * scale, 169 * scale, 102 * scale, 44 * scale), width=5)

        pygame.draw.rect(screen, (30, 218, 140), (369 * scale, 234 * scale, 60 * scale, 27 * scale), border_radius=8)
        screen.blit(Easy, (88 * scale, 180 * scale))
        screen.blit(Medium, (186 * scale, 180 * scale))
        screen.blit(Hard, (305 * scale, 180 * scale))

        screen.blit(Start, (378 * scale, 242 * scale))
        current_time = pygame.time.get_ticks()
        if current_time - last_update_time > 50:
            last_update_time = current_time
            if title_letter_index < len(chapter_info[1]):
                title_letter_index += 1
            if description_letter_index < len(chapter_info[2]):
                description_letter_index += 1
        pygame.display.update()

    pygame.quit()
