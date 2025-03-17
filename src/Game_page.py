import pygame
from snakes import Game
from Resouce import Buttons
from database import Retrieve_Question, update
from Result_2 import result
# from Menu import Menu


def Game_page(player_info, difficulties, return_menu, resource_path, chapter_info):
    pygame.init()
    print("Initial")
    running = True
    fullscreen = True
    color = (16, 196, 109)
    body_count = 3
    # player_info = eval(sys.argv[1])
    # difficulties = int(os.getenv("DIFFICULTIES", 8))

    settings = pygame.image.load(resource_path("assets/settings.png"))
    settings_size = pygame.transform.scale(settings, (128, 128))
    settings_rect = settings_size.get_rect(topleft=(1150, 13))
    user_answer = []

    screen = pygame.display.set_mode((1280, 800), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    is_alive = True
    game = Game(800, 412, screen, 1, 10000, resource_path)
    option = Buttons(screen, resource_path)
    open_setting = False
    game_over = False

    overlay = pygame.Surface((1280, 800), pygame.SRCALPHA)  # Enable per-pixel alpha
    overlay.fill((0, 0, 0, 130))  # RGBA: Black with 100/255 transparency

    coordinate = option._getCoordinate()
    button_a_x, button_a_y = coordinate[0]["x"], coordinate[0]["y"]
    button_b_x, button_b_y = coordinate[1]["x"], coordinate[1]["y"]
    button_c_x, button_c_y = coordinate[2]["x"], coordinate[2]["y"]
    button_d_x, button_d_y = coordinate[3]["x"], coordinate[3]["y"]
    font = pygame.font.Font(resource_path("assets/PeaberryBase.ttf"), 20)
    test = font.render("Hello, This is me, a person!", True, (30, 30, 30))

    Resume = pygame.image.load(resource_path("assets/Large_Buttons/Resume Button.png"))
    Resume_s = pygame.transform.scale(Resume, (Resume.get_width() / 3, Resume.get_height() / 3))
    Resume_rect = Resume_s.get_rect(topleft=(540, 125.97 * 2))

    Menu = pygame.image.load(resource_path("assets/Large_Buttons/Menu Button.png"))
    Menu_s = pygame.transform.scale(Menu, (Menu.get_width() / 3, Menu.get_height() / 3))
    Menu_rect = Resume_s.get_rect(topleft=(270 * 2, 180.93 * 2))

    Quit = pygame.image.load(resource_path("assets/Large_Buttons/Quit Button.png"))
    Quit_s = pygame.transform.scale(Quit, (Quit.get_width() / 3, Quit.get_height() / 3))
    Quit_rect = Resume_s.get_rect(topleft=(270 * 2, 242.09 * 2))

    Restart = pygame.image.load(resource_path("assets/Square_Buttons/Return Square Button.png"))
    fonts = pygame.font.Font(resource_path("assets/PeaberryBase.ttf"), 30)
    A_selection = fonts.render("A", True, (255, 255, 255))
    B_selection = fonts.render("B", True, (255, 255, 255))
    C_selection = fonts.render("C", True, (255, 255, 255))
    D_selection = fonts.render("D", True, (255, 255, 255))

    Restart_s = pygame.transform.scale(Restart, (Restart.get_width() / 3, Restart.get_height() / 3))
    Restart_rect = Restart_s.get_rect(topleft=(304.07 * 2, 294.8 * 2))
    Restart_rect_over = Restart_s.get_rect(topleft=((screen.get_width() - Restart_s.get_width()) / 2, 450))

    proceed = pygame.image.load(resource_path("assets/Square_Buttons/Play Square Button.png"))
    proceed_s = pygame.transform.scale(proceed, (proceed.get_width() / 3, proceed.get_height() / 3))
    proceed_rect = proceed_s.get_rect(topleft=(364.8 * 2, 294.8 * 2))
    proceed_rect_over = proceed_s.get_rect(topleft=(200 + (screen.get_width() - Restart_s.get_width()) / 2, 460))
    questions = 0
    list_Question = Retrieve_Question(chapter_info[0], "Question")
    print(list_Question)
    Option_title = Retrieve_Question(chapter_info[0], "Option1, Option2, Option3, Option4")
    print("Option Title: ", Option_title)
    answer = Retrieve_Question(chapter_info[0], "CorrectAnswer")
    game_over_text = fonts.render("GAME OVER", True, (255, 255, 255))
    hit = False
    player_proceed = False
    try:
        while running:
            screen.fill((50, 50, 50))
            text = font.render(f"{questions + 1}", True, (255, 255, 255))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and not game_over:
                        # Toggle fullscreen mode off
                        # if fullscreen:
                        #     screen = pygame.display.set_mode((640, 400))  # Windowed mode
                        #     fullscreen = False
                        #     running = False
                        # else:
                        #     screen = pygame.display.set_mode((1280, 800), pygame.FULLSCREEN)  # Back to fullscreen
                        #     fullscreen = True
                        print(running)
                        if open_setting:
                            open_setting = False
                            game.resume()
                        else:
                            open_setting = True
                            game.pause()  # Pause timer when opening the menu
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if game_over:
                        if Restart_rect_over.collidepoint(event.pos):
                            try:
                                body_count = 3
                                game = Game(800, 412, screen, 1, 10000, resource_path)  # Reinitialize the game
                                is_alive = True
                                open_setting = False
                                game_over = False
                                questions = 0
                                player_proceed = False
                                hit = False
                                user_answer.clear()
                                print("Restart")
                            except Exception as e:
                                print("Restart: ", e)
                        elif proceed_rect.collidepoint(event.pos) or proceed_rect_over.collidepoint(event.pos):
                            print("Proceed..")
                            try:
                                print(player_info[0])
                                # Update the player's level in the database
                                if int(chapter_info[3]) >= int(player_info[3]):
                                    update("[User]", "[Level]", int(player_info[3]) + 1, player_info[0])
                                result(chapter_info, user_answer, resource_path, return_menu, player_info)
                            except Exception as e:
                                print("Error: ", e)
                            # running = False
                            pygame.display.quit()
                            # sys.exit()
                    else:
                        if settings_rect.collidepoint(event.pos):
                            open_setting = True
                            game.pause()
                        elif Resume_rect.collidepoint(event.pos):
                            print("Resume")
                            open_setting = False
                            game.resume()
                        elif Menu_rect.collidepoint(event.pos):
                            print("Menu")
                            # Menu(player_info)
                            # return_menu(True, player_info, return_menu)
                            return_menu(player_info)
                            running = False
                        elif Restart_rect.collidepoint(event.pos):
                            try:
                                body_count = 3
                                game = Game(800, 412, screen, 1, 10000, resource_path)  # Reinitialize the game
                                is_alive = True
                                open_setting = False
                                game_over = False
                                questions = 0
                                player_proceed = False
                                hit = False
                                user_answer.clear()
                                print("Restart")
                            except Exception as e:
                                print("Error restart: ", e)
                        elif Quit_rect.collidepoint(event.pos):
                            print("Quit")
                            print("Quit_rect position:", Quit_rect.topleft)
                            print("Restart_rect_over position:", Restart_rect_over.topleft)
                            running = False

            if not fullscreen:
                pygame.draw.rect(screen, (0, 0, 0), (29, 27, 250, 340), border_radius=5)
                pygame.draw.rect(screen, (217, 217, 217), (29, 27, 250, 10.85),
                                 border_top_left_radius=5, border_top_right_radius=5)
                pygame.draw.rect(screen, color, (29, 27, 250, 10.85),
                                 border_top_left_radius=5, border_top_right_radius=5)
                pygame.draw.rect(screen, (103, 111, 147), (114 / 2, 98 / 2, 388 / 2, 208 / 2), border_radius=5)
                pygame.draw.rect(screen, (255, 141, 28), (37, 174, 234, 30), border_radius=5)
                pygame.draw.rect(screen, (28, 69, 255), (37, 221, 234, 30), border_radius=5)
                pygame.draw.rect(screen, (75, 71, 67), (37, 268, 234, 30), border_radius=5)
                pygame.draw.rect(screen, (120, 104, 89), (37, 315, 234, 30), border_radius=5)

                # Playground
                pygame.draw.rect(screen, (75, 174, 78), (340.21, 47.87, (40 * 6), (40 * 7)), border_radius=5)
                pygame.draw.rect(screen, (124, 93, 35), (340.21, 47.87, (40 * 6), (40 * 7)), width=5, border_radius=5)
                game._update(0.5, body_count, True)
                game._draw(0.5)
            else:

                position = game._getPosition()
                pygame.draw.rect(screen, (0, 0, 0), (58, 54, 500, 680), border_radius=5)
                pygame.draw.rect(screen, (217, 217, 217), (29 * 2, 27 * 2, 250 * 2, 10.85 * 2),
                                 border_top_left_radius=5, border_top_right_radius=5)
                if game._TimeBar():
                    is_alive = False
                    game_over = True
                # pygame.draw.rect(screen, color, (29 * 2, 27 * 2, 250 * 2, 10.85 * 2),
                #                  border_top_left_radius=5, border_top_right_radius=5)
                pygame.draw.rect(screen, (103, 111, 147), (114, 98, 388, 208), border_radius=5)
                pygame.draw.rect(screen, (255, 141, 28), (60 * 2, 174 * 2, 211 * 2, 30 * 2), border_radius=5)
                pygame.draw.rect(screen, (28, 69, 255), (60 * 2, 221 * 2, 211 * 2, 30 * 2), border_radius=5)
                pygame.draw.rect(screen, (75, 71, 67), (60 * 2, 268 * 2, 211 * 2, 30 * 2), border_radius=5)
                pygame.draw.rect(screen, (120, 104, 89), (60 * 2, 315 * 2, 211 * 2, 30 * 2), border_radius=5)

                screen.blit(settings_size, (1150, 13))
                # Playground
                pygame.draw.rect(screen, (75, 174, 78), (340 * 2, 46 * 2, 220 * 2, 300 * 2), border_radius=5)
                pygame.draw.rect(screen, (124, 93, 35), (340 * 2, 46 * 2, 220 * 2, 300 * 2), width=5,
                                 border_radius=5)

                if position:
                    if position[0] < 620 + 40 or position[0] > 1120 - 40:
                        is_alive = False
                        game_over = True
                    elif position[1] < 82 or position[1] > 692 - 40:
                        is_alive = False
                        game_over = True
                    else:
                        hit = option.check_collision(position)  # Check for collisions with buttons

                try:
                    if hit:
                        game.timer_started = False
                        if questions >= 10:
                            screen.blit(text, (75, 100))
                        else:
                            screen.blit(text, (80, 100))
                        questions += 1
                        game.time_bar_start = pygame.time.get_ticks()
                        if answer[questions - 1] == hit:
                            body_count += 1
                            user_answer.append(True)
                        else:
                            user_answer.append(False)
                    else:
                        if questions >= 10:
                            screen.blit(text, (75, 100))
                        else:
                            screen.blit(text, (80, 100))
                    Question_title = game._animated_text(list_Question[questions],
                                                         font, 106, 98, 20, 388)
                    game._draw(1)

                    screen.blit(A_selection, (85, 363))
                    screen.blit(B_selection, (85, 456))
                    screen.blit(C_selection, (85, 551))
                    screen.blit(D_selection, (85, 645))

                    if Question_title:
                        game._animated_text(Option_title[questions][0],
                                            font, 125, 353, 5, 422)
                        game._animated_text(Option_title[questions][1],
                                            font, 125, 444, 5, 422)
                        game._animated_text(Option_title[questions][2],
                                            font, 125, 538, 5, 422)
                        done = game._animated_text(Option_title[questions][3],
                                                   font, 125, 632, 5, 422)

                        if not open_setting and done:
                            if not game.timer_started:
                                game.time_bar_start = pygame.time.get_ticks()  # Start timer here
                                game.timer_started = True
                            game._update(1, body_count, is_alive)

                except IndexError:
                    # open_setting = True
                    game_over = True
                option._draw()

                # if open_setting[1]:
                #     screen.blit(overlay, (0, 0))
                #     pygame.draw.rect(screen, (47, 47, 47), (450, 100, ((screen.get_width() - 450) / 2
                #                                                        , (screen.get_height() - 100) / 2)))
                if open_setting:
                    screen.blit(overlay, (0, 0))
                    pygame.draw.rect(screen, (47, 47, 47), (216.47 * 2, 67.88 * 2, 197.75 * 2, 264.24 * 2))
                    screen.blit(Resume_s, (270 * 2, 125.97 * 2))
                    screen.blit(Menu_s, (270 * 2, 180.93 * 2))
                    screen.blit(Restart_s, (304.07 * 2, 294.8 * 2))
                    screen.blit(Quit_s, (270 * 2, 242.09 * 2))
                    if player_proceed:
                        screen.blit(proceed_s, (364.07 * 2, 294.8 * 2))
                if game_over:
                    screen.blit(overlay, (0, 0))
                    pygame.draw.rect(screen, (47, 47, 47), ((screen.get_width() - 650) / 2, (screen.get_height() - 300) / 2
                                                            , 650, 300))
                    screen.blit(game_over_text, ((screen.get_width() - game_over_text.get_width()) / 2, 365))
                    screen.blit(Restart_s, ((screen.get_width() - Restart_s.get_width()) / 2, 450))
                    if int(len(answer) / 2) <= user_answer.count(True):
                        player_proceed = True
                    if player_proceed:
                        screen.blit(proceed_s, (200 + (screen.get_width() - proceed_s.get_width()) / 2, 450))

            pygame.display.update()
            clock.tick(difficulties)
    except Exception as f:
        print("Something went wrong: ", f)
    pygame.quit()
