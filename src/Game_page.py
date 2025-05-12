import pygame
from snakes import Game
from Resouce import Buttons
from database import Retrieve_Question, update, resultDB
from Result import result
from datetime import datetime
# from Menu import Menu


def Game_page(player_info, difficulties, return_menu, resource_path, chapter_info, quiz_level, click):
    pygame.init()
    running = True
    color = (16, 196, 109)
    body_count = 3
    scale = 1.25
    # player_info = eval(sys.argv[1])
    # difficulties = int(os.getenv("DIFFICULTIES", 8))

    settings = pygame.image.load(resource_path("assets/settings.png"))
    pygame.mixer.music.load(resource_path("assets/Gameplay_audio.mp3"))
    pygame.mixer.music.play(loops=True)
    settings_size = pygame.transform.scale(settings, (128 * scale, 128 * scale))
    settings_rect = settings_size.get_rect(topleft=(1150 * scale, 13 * scale))
    user_answer = []

    screen = pygame.display.set_mode((1280, 800), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    is_alive = True
    game = Game(800 * scale, 412 * scale, screen, 1, 10000, resource_path, difficulties)

    option = Buttons(screen, resource_path)
    open_setting = False
    game_over = False

    overlay = pygame.Surface((1600, 1000), pygame.SRCALPHA)  # Enable per-pixel alpha
    overlay.fill((0, 0, 0, 130))  # RGBA: Black with 100/255 transparency

    coordinate = option._getCoordinate()
    button_a_x, button_a_y = coordinate[0]["x"], coordinate[0]["y"]
    button_b_x, button_b_y = coordinate[1]["x"], coordinate[1]["y"]
    button_c_x, button_c_y = coordinate[2]["x"], coordinate[2]["y"]
    button_d_x, button_d_y = coordinate[3]["x"], coordinate[3]["y"]
    font = pygame.font.Font(resource_path("assets/PeaberryBase.ttf"), 23)

    Resume = pygame.image.load(resource_path("assets/Large_Buttons/Resume Button.png"))
    Resume_s = pygame.transform.scale(Resume, (scale * Resume.get_width() / 3, scale *  Resume.get_height() / 3))
    Resume_rect = Resume_s.get_rect(topleft=(scale * 540, scale * 125.97 * 2))

    Menu = pygame.image.load(resource_path("assets/Large_Buttons/Menu Button.png"))
    Menu_s = pygame.transform.scale(Menu, (scale * Menu.get_width() / 3, scale * Menu.get_height() / 3))
    Menu_rect = Resume_s.get_rect(topleft=(scale * 270 * 2, scale * 180.93 * 2))

    Quit = pygame.image.load(resource_path("assets/Large_Buttons/Quit Button.png"))
    Quit_s = pygame.transform.scale(Quit, (scale * Quit.get_width() / 3, scale * Quit.get_height() / 3))
    Quit_rect = Resume_s.get_rect(topleft=(scale * 270 * 2, scale * 242.09 * 2))

    Restart = pygame.image.load(resource_path("assets/Square_Buttons/Return Square Button.png"))
    fonts = pygame.font.Font(resource_path("assets/PeaberryBase.ttf"), 30)
    A_selection = fonts.render("A", True, (255, 255, 255))
    B_selection = fonts.render("B", True, (255, 255, 255))
    C_selection = fonts.render("C", True, (255, 255, 255))
    D_selection = fonts.render("D", True, (255, 255, 255))

    Restart_s = pygame.transform.scale(Restart, (scale * Restart.get_width() / 3, scale * Restart.get_height() / 3))
    Restart_rect = Restart_s.get_rect(topleft=(scale * 304.07 * 2, scale * 294.8 * 2))
    Restart_rect_over = Restart_s.get_rect(topleft=((screen.get_width() - Restart_s.get_width()) / 2,
                                                    scale * 450))

    proceed = pygame.image.load(resource_path("assets/Square_Buttons/Play Square Button.png"))
    proceed_s = pygame.transform.scale(proceed, (scale * proceed.get_width() / 3, scale * proceed.get_height() / 3))
    proceed_rect = proceed_s.get_rect(topleft=(scale * 364.8 * 2, scale * 294.8 * 2))
    proceed_rect_over = proceed_s.get_rect(topleft=(scale * 200 + (screen.get_width() - Restart_s.get_width()) / 2,
                                                    scale * 460))
    questions = 0
    print("From GamePage: ", chapter_info[0])
    list_Question = Retrieve_Question(chapter_info[0][3:], "Question")
    Option_title = Retrieve_Question(chapter_info[0][3:], "Option1, Option2, Option3, Option4")

    answer = Retrieve_Question(chapter_info[0][3:], "CorrectAnswer")
    game_over_text = fonts.render("GAME OVER", True, (255, 255, 255))
    hit = False
    player_proceed = False
    death_sound_played = False
    set_str = datetime.now().strftime('%H:%M:%S')
    set_time = datetime.strptime(set_str, "%H:%M:%S")  # convert to datetime
    game.time_bar_start = pygame.time.get_ticks()
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
                        if open_setting:
                            open_setting = False
                            game.resume()
                        else:
                            open_setting = True
                            game.pause()  # Pause timer when opening the menu
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    click.play()
                    if game_over:
                        if Restart_rect_over.collidepoint(event.pos):
                            try:
                                body_count = 3
                                game = Game(800 * scale, 412 * scale, screen, 1, 10000, resource_path, difficulties)
                                # Reinitialize the game
                                is_alive = True
                                open_setting = False
                                game_over = False
                                questions = 0
                                player_proceed = False
                                death_sound_played = False
                                hit = False
                                user_answer.clear()
                                print("Restart")
                            except Exception as e:
                                print("Restart: ", e)
                        elif proceed_rect.collidepoint(event.pos) or proceed_rect_over.collidepoint(event.pos):
                            print("Proceed..")
                            try:
                                print(f"checking: {quiz_level}, {player_info[4]}")
                                print(player_info[0])
                                if quiz_level >= int(player_info[4]) and int(chapter_info[-2][3:]) != 10:
                                    update("[Student]", "[Level]", int(player_info[4]) + 1,
                                           player_info[0], "Student")
                                resultDB(player_info[0], quiz_level, chapter_info, user_answer, difficulties, set_time)
                                result(chapter_info, user_answer, resource_path, return_menu, player_info[0])
                                # Update the player's level in the database
                                pygame.mixer.music.stop()
                            except Exception as e:
                                print("Error: ", e)
                            # running = False
                            pygame.display.quit()
                            # sys.exit()
                    else:
                        if settings_rect.collidepoint(event.pos):
                            print("HAi")
                            open_setting = True
                            game.pause()
                        elif Resume_rect.collidepoint(event.pos):
                            print("Resume")
                            open_setting = False
                            game.resume()
                        elif Menu_rect.collidepoint(event.pos):
                            print("Menu")
                            pygame.mixer.music.stop()
                            # Menu(player_info)
                            # return_menu(True, player_info, return_menu)
                            running = False
                            return_menu(player_info)
                        elif Restart_rect.collidepoint(event.pos):
                            try:
                                body_count = 3
                                game = Game(800 * scale, 412 * scale, screen, 1, 10000, resource_path, difficulties)  # Reinitialize the game
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
                            running = False

            position = game._getPosition()
            pygame.draw.rect(screen, (0, 0, 0), (58 * scale, 54 * scale,
                                                 500 * scale, 680 * scale), border_radius=5)
            pygame.draw.rect(screen, (217, 217, 217), (29 * 2 * scale, 27 * 2 * scale,
                                                       250 * 2 * scale, 10.85 * 2 * scale),
                             border_top_left_radius=5, border_top_right_radius=5)
            if game._TimeBar():
                is_alive = False
                [user_answer.append(False) for i in range(len(answer) - len(user_answer))]
                game_over = True
            game.pause()
            # pygame.draw.rect(screen, color, (29 * 2, 27 * 2, 250 * 2, 10.85 * 2),
            #                  border_top_left_radius=5, border_top_right_radius=5)
            pygame.draw.rect(screen, (103, 111, 147), (114 * scale, 98 * scale,
                                                       388 * scale, 208 * scale), border_radius=5)
            pygame.draw.rect(screen, (255, 141, 28), (60 * 2 * scale, 174 * 2 * scale,
                                                      211 * 2 * scale, 30 * 2 * scale), border_radius=5)
            pygame.draw.rect(screen, (28, 69, 255), (60 * 2 * scale, 221 * 2 * scale,
                                                     211 * 2 * scale, 30 * 2 * scale), border_radius=5)
            pygame.draw.rect(screen, (75, 71, 67), (60 * 2 * scale, 268 * 2 * scale,
                                                    211 * 2 * scale, 30 * 2 * scale), border_radius=5)
            pygame.draw.rect(screen, (120, 104, 89), (60 * 2 * scale, 315 * 2 * scale,
                                                      211 * 2 * scale, 30 * 2 * scale), border_radius=5)

            screen.blit(settings_size, (1150 * scale, 13 * scale))
            # Playground
            pygame.draw.rect(screen, (75, 174, 78), (340 * 2 * scale, 46 * 2 * scale,
                                                     220 * 2 * scale, 300 * 2 * scale), border_radius=5)
            pygame.draw.rect(screen, (124, 93, 35), (340 * 2 * scale, 46 * 2 * scale,
                                                     220 * 2 * scale, 300 * 2 * scale), width=5,
                             border_radius=5)

            if position:
                if (position[0] < scale * (620 + 40) or position[0] > scale * (1120 - 40) or position[1] < scale * 82 or
                        position[1] > scale * (692 - 40)):
                    is_alive = False
                    game_over = True
                    if not death_sound_played:
                        game.snake.death_sound.play()
                        death_sound_played = True  # ✅ Prevent future replays

                    [user_answer.append(False) for i in range(len(answer) - len(user_answer))]
                else:
                    hit = option.check_collision(position)  # Check for collisions with buttons

            try:
                if hit:
                    game.timer_started = False
                    if questions >= 10:
                        screen.blit(text, (scale * 75, scale * 100))
                    else:
                        screen.blit(text, (scale * 80, scale * 100))
                    questions += 1
                    game.time_bar_start = pygame.time.get_ticks()

                    if answer[questions - 1] == hit:
                        body_count += 1
                        user_answer.append(True)
                    else:
                        user_answer.append(False)
                else:
                    if questions >= 10:
                        screen.blit(text, (scale * 75, scale * 100))
                    else:
                        screen.blit(text, (scale * 80, scale * 100))
                Question_title = game._animated_text(list_Question[questions],
                                                     font, scale * 106, scale * 98, scale * 20, scale * 388)
                game._draw(1.25)

                screen.blit(A_selection, (85 * scale, 363 * scale))
                screen.blit(B_selection, (85 * scale, 456 * scale))
                screen.blit(C_selection, (85 * scale, 551 * scale))
                screen.blit(D_selection, (85 * scale, 645 * scale))

                if Question_title:
                    done1 = game._animated_text(Option_title[questions][0],
                                        font, scale * 125, scale * 353, 0, scale * 422)
                    done2 = game._animated_text(Option_title[questions][1],
                                        font, scale * 125, scale * 444, 5, scale * 422)
                    done3 = game._animated_text(Option_title[questions][2],
                                        font, scale * 125, scale * 538, 5, scale * 422)
                    done4 = game._animated_text(Option_title[questions][3],
                                               font, scale * 125, scale * 632, 5, scale * 422)

                    if not open_setting and (done1 and done2 and done3 and done4):
                        # if not game.timer_started:
                        #     game.time_bar_start = pygame.time.get_ticks()  # Start timer here
                        #     game.timer_started = True
                        game._update(scale, body_count, is_alive)
                        game.resume()

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
                pygame.draw.rect(screen, (47, 47, 47), (216.47 * 2 * scale, 67.88 * 2 * scale,
                                                        197.75 * 2 * scale, 264.24 * 2 * scale))
                screen.blit(Resume_s, (270 * 2 * scale, 125.97 * 2 * scale))
                screen.blit(Menu_s, (270 * 2 * scale, 180.93 * 2 * scale))
                screen.blit(Restart_s, (304.07 * 2 * scale, 294.8 * 2 * scale))
                screen.blit(Quit_s, (270 * 2 * scale, 242.09 * 2 * scale))
                if player_proceed:
                    screen.blit(proceed_s, (364.07 * 2 * scale, 294.8 * 2 * scale))
            if game_over:
                screen.blit(overlay, (0, 0))
                pygame.draw.rect(screen, (47, 47, 47), ((screen.get_width() - scale * 650) / 2,
                                                        (screen.get_height() - scale * 300) / 2
                                                        , scale * 650, scale * 300))
                screen.blit(game_over_text, ((screen.get_width() - game_over_text.get_width()) / 2, scale * 365))
                screen.blit(Restart_s, ((screen.get_width() - Restart_s.get_width()) / 2, scale * 450))
                if int(len(answer) / 2) <= user_answer.count(True):
                    player_proceed = True
                if player_proceed:
                    screen.blit(proceed_s, (scale * 200 + (screen.get_width() - proceed_s.get_width()) / 2,
                                            scale * 450))

            pygame.display.update()
            # clock.tick(difficulties)
    except Exception as f:
        print("Something went wrong: ", f)
    pygame.quit()