import hashlib
import json
import os
import sys

import pygame
import random

from PIL import Image

from database import select, update_DB
from OTP import send_otp_email as otp


class Option:
    def __init__(self, resource_path):
        # Load button images
        self.blue_A = pygame.image.load(resource_path("assets/MV_Icons_Letter_Buttons/Buttons/blue-A.png"))
        self.blue_A_push = pygame.image.load(resource_path("assets/MV_Icons_Letter_Buttons/Buttons/blue-A-pushed.png"))

        self.green_B = pygame.image.load(resource_path("assets/MV_Icons_Letter_Buttons/Buttons/green-B.png"))
        self.green_B_push = pygame.image.load(
            resource_path("assets/MV_Icons_Letter_Buttons/Buttons/green-B-pushed.png"))

        self.red_C = pygame.image.load(resource_path("assets/MV_Icons_Letter_Buttons/Buttons/red-C.png"))
        self.red_C_push = pygame.image.load(resource_path("assets/MV_Icons_Letter_Buttons/Buttons/red-C-pushed.png"))

        self.yellow_D = pygame.image.load(resource_path("assets/MV_Icons_Letter_Buttons/Buttons/yellow-D.png"))
        self.yellow_D_push = pygame.image.load(
            resource_path("assets/MV_Icons_Letter_Buttons/Buttons/yellow-D-pushed.png"))

        used_positions = set()

        self.buttons = []
        for button_info in [
            {"image": self.blue_A, "pushed_image": self.blue_A_push, "name": "A"},
            {"image": self.green_B, "pushed_image": self.green_B_push, "name": "B"},
            {"image": self.red_C, "pushed_image": self.red_C_push, "name": "C"},
            {"image": self.yellow_D, "pushed_image": self.yellow_D_push, "name": "D"},
        ]:
            while True:
                # Generate a random position
                x = random.randrange(680, 1020, 40)
                y = random.randrange(92, 692, 40)
                position = (x, y)

                # Check if the position is already used
                if position not in used_positions:
                    print("Overlap")
                    used_positions.add(position)  # Mark this position as used
                    break  # Exit the loop once a unique position is found

            # Add the button with the unique position
            self.buttons.append({
                "image": button_info["image"],
                "pushed_image": button_info["pushed_image"],
                "x": x,
                "y": y,
                "name": button_info["name"]
            })

        self.frame_duration = 5  # Number of seconds to display each frame
        self.frame_timer = 0  # Tracks time since last frame switch
        self.current_state = "normal"  # Tracks whether buttons are in normal or pushed state

    def update(self, dt):
        """Update the animation state."""
        self.frame_timer += dt / 5000  # Convert milliseconds to seconds
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0  # Reset the timer
            # Toggle between normal and pushed states
            if self.current_state == "normal":
                self.current_state = "pushed"
            else:
                self.current_state = "normal"

    def draw(self, screen):
        """Draw the buttons on the screen."""
        # Draw the buttons
        for button in self.buttons:
            if self.current_state == "normal":
                screen.blit(button["image"], (button["x"], button["y"]))
            else:
                screen.blit(button["pushed_image"], (button["x"], button["y"]))

    def reset_button_positions(self):
        """Reset button positions to new random coordinates without overlapping."""
        used_positions = set()
        for button in self.buttons:
            while True:
                x = random.randrange(680, 1020, 40)
                y = random.randrange(92, 692, 40)
                position = (x, y)
                if position not in used_positions:
                    used_positions.add(position)
                    button["x"] = x
                    button["y"] = y
                    break


class Buttons:
    def __init__(self, screen, resource_path):
        self.screen = screen
        self.options = Option(resource_path)
        self.clock = pygame.time.Clock()
        self.last_update_time = 0  # Track the last update time for buttons

    def _draw(self):
        """Update and draw the buttons at 3 FPS."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time >= 1000 // 3:  # 3 FPS
            self.last_update_time = current_time
            self.options.update(1000 // 3)  # Update buttons
            self.options.draw(self.screen)  # Draw buttons
        else:
            self.options.update(1000 // 3)  # Update buttons
            self.options.draw(self.screen)  # Draw buttons

    def _getCoordinate(self):
        return self.options.buttons

    def check_collision(self, position):
        """Check if the snake's head collides with any button."""
        for button in self.options.buttons:
            if position[0] == button["x"] and position[1] == button["y"]:
                print(button["name"])  # Print the button's name (A, B, C, or D)
                self.options.reset_button_positions()  # Reset button positions
                return button["name"]
        return False


def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def font(size):
    return pygame.font.Font(resource_path("assets/PeaberryBase.ttf"), size)


def spacing(text):
    return -15 if len(str(text)) == 1 else -5


def load():
    if os.path.exists("user_credentials.json"):
        with open("user_credentials.json", "r") as file:
            return json.load(file)


class Profile:
    def __init__(self, screen, student_info):
        self.screen = screen
        self.student_info = student_info
        self.easy = resource_path("assets/Difficulties_Icons/Easy.png")
        self.medium = resource_path("assets/Difficulties_Icons/Medium.png")
        self.hard = resource_path("assets/Difficulties_Icons/Hard.png")
        self.scale = 2.3
        self.name = font(30).render(str(self.student_info[1]), True, (255, 255, 255))
        self.quiz = font(30).render(str(self.student_info[4]), True, (255, 255, 255))
        self.y_offset = [50 * self.scale, 48 * self.scale]
        self.x_offset = 70 * self.scale
        self.list_records = []
        self.overlay = pygame.Surface((1280, 800), pygame.SRCALPHA)  # Enable per-pixel alpha
        self.overlay_rect = self.overlay.get_rect(topleft=(0, 0))
        self.Timestamp_col = font(20).render("Time Taken", True, (0, 0, 0))
        self.scroll_offset = 0
        self.max_scroll = 0
        self.Logout = pygame.image.load(resource_path("assets/icons/cHedrNavLogoutBtn.png"))
        self.Logout_resize = pygame.transform.scale(self.Logout, (64, 64))
        self.logout_rect = self.Logout_resize.get_rect(topleft=(1005, 113))
        self.open_profile = [False, False]
        self.list_avatar = []
        self.img = load()["img"] if os.path.exists("user_credentials.json") else None
        print(self.img)
        self.history_rect = pygame.Rect(
            (self.screen.get_width() - 401 * self.scale) / 2,
            120 * self.scale + 100,
            401 * self.scale,
            153 * self.scale
        )
        self.change_rect = pygame.Rect(872, 221, 225, 50)
        self.center = ((self.screen.get_width() - 336.44 * self.scale) / 2, 90 * self.scale)
        self.profile_rect = pygame.Rect(
            self.center[0] - 64.56,
            self.center[1] - 64.56,
            64.56 * 2,
            64.56 * 2
        )

    def handle_click(self, mouse_pos):
        profile_box = pygame.Rect(120, 81, 1157 - 120, 738 - 81)
        select_box = pygame.Rect(333, 261, 661, 343)
        if self.overlay_rect.collidepoint(mouse_pos):
            if self.open_profile[1]:
                if not select_box.collidepoint(mouse_pos):
                    self.open_profile[1] = False

            elif not profile_box.collidepoint(mouse_pos):
                self.open_profile[0] = False

        if self.profile_rect.collidepoint(mouse_pos) and self.open_profile[0]:
            self.open_profile[1] = True
        if self.open_profile[1]:
            for index, rect in enumerate(self.list_avatar):
                if rect.collidepoint(mouse_pos):
                    print(f"Clicked on avatar {index}")
                    update = load()
                    update["img"] = f"Pic{index + 1}.png"
                    self.img = update["img"]
                    with open("user_credentials.json", "w") as file:
                        json.dump(update, file)
                    return

    def records(self):
        count = 0
        pygame.init()
        self.list_records = []
        try:
            game_session = select(f"select top 15 * from Game_Session where StudentID = '{self.student_info[0]}' "
                                  f"ORDER BY CAST(SUBSTRING(GameID, 3, LEN(GameID) - 2) AS INT) DESC")
        except Exception as e:
            print(e)
        self.max_scroll = max(0, (len(game_session) - 3) * self.y_offset[0])
        for index, i in enumerate(game_session):
            container_y = 130 * self.scale + 100 + (self.y_offset[0] * index) - self.scroll_offset  # Add scroll offset
            # Only draw if visible in history container
            if container_y + 37 * self.scale < self.history_rect.top or container_y > self.history_rect.bottom:
                continue
            rect = pygame.Rect((self.screen.get_width() - 373 * self.scale) / 2,
                               container_y,
                               353 * self.scale,
                               37 * self.scale)
            self.list_records.append((rect, index))
            # Records container
            pygame.draw.rect(self.screen, (59, 59, 59), ((self.screen.get_width() - 373 * self.scale) / 2,
                                                         container_y,
                                                         353 * self.scale,
                                                         37 * self.scale), border_radius=4)
            container_height = 37 * self.scale
            container_center_y = container_y + container_height / 2
            level = font(20).render(str(i[1]), True, (255, 255, 255))
            level_y = container_center_y - (level.get_height() / 2)

            results = select(f"select * from Result where GameID = '{i[0]}'")
            questions = font(20).render(str(len(results)), True, (255, 255, 255))
            questions_y = container_center_y - (questions.get_height() / 2)
            for counting in results:
                if counting[-1] == '1':
                    count += 1

            correct = font(20).render(str(count), True, (255, 255, 255))
            correct_y = container_center_y - (correct.get_height() / 2)
            count = 0
            timestamp = font(20).render(str(i[-1]), True, (255, 255, 255))
            timestamp_y = container_center_y - (timestamp.get_height() / 2)
            difficulty_icon_path = (
                self.easy if i[3] == "Easy" else
                self.medium if i[3] == "Medium" else
                self.hard
            )
            # Icons pic
            icons = pygame.image.load(difficulty_icon_path)
            icon_y = container_center_y - (30 * self.scale / 2)
            d_icons = pygame.transform.scale(icons, (70, 70))
            self.screen.blit(d_icons, (35.72 * self.scale + 169,
                                       icon_y))

            self.screen.blit(level, (121.28 * self.scale + 162, level_y))
            self.screen.blit(questions, (121.28 * self.scale + (self.x_offset * 1) + 165 + spacing(len(results)),
                                         questions_y))
            self.screen.blit(correct, (121.28 * self.scale + (self.x_offset * 2) + 169 + spacing(count),
                                       correct_y))
            self.screen.blit(timestamp, (876 + (137 - timestamp.get_width()) / 2, timestamp_y))

    def select_avatar(self):
        self.overlay.fill((0, 0, 0, 130))
        self.screen.blit(self.overlay, (0, 0))
        pygame.draw.rect(self.screen, (69, 69, 69), (333, 261, 661, 343))
        # Path to image folder
        try:
            image_folder = resource_path("assets/Avatar/")

            # List all files in the folder
            image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg'))]

            # Load and resize all images
            all_pics = []
            for filename in image_files:
                full_path = os.path.join(image_folder, filename)
                try:
                    # Load and scale the image
                    image = pygame.image.load(full_path).convert_alpha()
                    resized_image = pygame.transform.scale(image, (90, 90))
                    size = resized_image.get_size()

                    # Create a circular mask
                    mask_surface = pygame.Surface(size, pygame.SRCALPHA)
                    pygame.draw.circle(mask_surface, (255, 255, 255, 255), (size[0] // 2, size[1] // 2), min(size) // 2)

                    # Apply mask to the resized image
                    circular_image = resized_image.copy()
                    circular_image.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    all_pics.append(circular_image)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                    continue

            # Display all images in a row
            for index, img in enumerate(all_pics):
                self.list_avatar.append(pygame.Rect(382 + index * 130, 306, 90, 90))
                self.screen.blit(img, (382 + index * 130, 306))
        except Exception as e:
            print("What: ", e)

    def _draw(self):
        self.overlay.fill((0, 0, 0, 130))
        self.screen.blit(self.overlay, (0, 0))
        pygame.draw.rect(self.screen, (69, 69, 69), ((self.screen.get_width() - 450 * self.scale) / 2,
                                                     (self.screen.get_height() - 275 * self.scale) / 2,
                                                     450 * self.scale,
                                                     285 * self.scale), border_radius=4)
        self.screen.blit(self.name, (155 * self.scale, 65 * self.scale))
        Logout = pygame.image.load(resource_path("assets/icons/cHedrNavLogoutBtn.png"))
        Logout_resize = pygame.transform.scale(Logout, (64, 64))
        self.screen.blit(Logout_resize, (1005, 113))
        if bool(self.img):
            try:
                full_path = resource_path(f"assets/Avatar/{self.img}")
                image = pygame.image.load(full_path).convert_alpha()
                resized_image = pygame.transform.scale(image, (128, 128))
                size = resized_image.get_size()

                # Create a circular mask
                mask_surface = pygame.Surface(size, pygame.SRCALPHA)
                pygame.draw.circle(mask_surface, (255, 255, 255, 255), (size[0] // 2, size[1] // 2), min(size) // 2)

                # Apply mask to the resized image
                circular_image = resized_image.copy()
                circular_image.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                self.screen.blit(circular_image, (206, 166))
            except Exception as e:
                print("What is: ", e)
        else:
            pygame.draw.circle(self.screen, (217, 217, 217), (253.904, 207), 64.56)
        # Header container
        pygame.draw.rect(self.screen, (126, 122, 122), ((self.screen.get_width() - 401 * self.scale) / 2,
                                                        93 * self.scale + 100,
                                                        401 * self.scale, 18 * self.scale), border_radius=4)

        pygame.draw.rect(self.screen, (0, 131, 96), self.change_rect, border_radius=2)
        change_password = font(20).render("Change Password", True, (255, 255, 255))
        self.screen.blit(change_password, (872 + (225 - change_password.get_width()) / 2,
                                           221 + (50 - change_password.get_height()) / 2))
        # History container
        pygame.draw.rect(self.screen, (126, 122, 122), self.history_rect, border_radius=4)
        # Set clipping area
        clip_rect = self.history_rect.copy()
        clip_rect.height -= 20  # Adjust if needed
        self.screen.set_clip(clip_rect)
        # Reset clipping
        self.records()
        self.screen.set_clip(None)

        difficulties = font(20).render("Difficulties", True, (0, 0, 0))
        Level = font(20).render("Level", True, (0, 0, 0))
        Questions = font(20).render("Questions", True, (0, 0, 0))
        Correct = font(20).render("Correct", True, (0, 0, 0))

        self.screen.blit(difficulties, (30 * self.scale + 165, 96 * self.scale + 100))
        self.screen.blit(Level, (110 * self.scale + 165, 96 * self.scale + 100))
        self.screen.blit(Questions, (165 * self.scale + 165, 96 * self.scale + 100))
        self.screen.blit(Correct, (243 * self.scale + 165, 96 * self.scale + 100))
        self.screen.blit(self.Timestamp_col, (307 * self.scale + 165, 96 * self.scale + 100))

        self.draw_scrollbar()

    def draw_scrollbar(self):
        if self.max_scroll > 0:
            # Calculate scrollbar dimensions
            scrollbar_width = 10
            scrollbar_height = (self.history_rect.height ** 2) / (self.history_rect.height + self.max_scroll)
            scrollbar_y = self.history_rect.top + (self.scroll_offset / self.max_scroll) * (
                    self.history_rect.height - scrollbar_height)

            # Draw scrollbar track
            pygame.draw.rect(self.screen, (100, 100, 100),
                             (self.history_rect.right - scrollbar_width - 2,
                              self.history_rect.top,
                              scrollbar_width,
                              self.history_rect.height),
                             border_radius=5)

            # Draw scrollbar thumb
            pygame.draw.rect(self.screen, (200, 200, 200),
                             (self.history_rect.right - scrollbar_width - 2,
                              scrollbar_y,
                              scrollbar_width,
                              scrollbar_height),
                             border_radius=5)

    def page(self):
        if self.open_profile[0]:
            self._draw()
        if self.open_profile[1]:
            self.select_avatar()


def countdown(start_time, duration=60):
    elapsed_ms = pygame.time.get_ticks() - start_time
    elapsed_sec = elapsed_ms // 1000
    return max(0, duration - elapsed_sec)


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


class Keyboard_Writing:
    def __init__(self, screen, user_info, max_length=30):
        self.user_info = user_info
        self.pin = None
        self.placeholder = "Password"
        self.placeholder2 = "Confirm Password"  # Placeholder for input2
        self.active_input = 1  # 1 for input_rect1, 2 for input_rect2
        self.text = ""
        self.text2 = ""  # Text for the second input
        self.font = font(30)
        self.scale = 2.3
        self.max_length = max_length
        self.overlay = pygame.Surface((1280, 800), pygame.SRCALPHA)  # Enable per-pixel alpha
        self.overlay_rect = self.overlay.get_rect(topleft=(0, 0))
        self.txt_surface = self.font.render(self.placeholder, True, (255, 255, 255))
        self.screen = screen
        self.textfield_width = 0
        self.proceed_txt = ""
        self.shake = True
        self.frame_timer = 0
        self.last_update_time = 0
        self.input_x = (self.screen.get_width() - 271 * self.scale) / 2 + (241 * self.scale - 420) / 2
        self.input_y = (self.screen.get_height() - 151 * self.scale) / 2 + 70
        self.input_rect = pygame.Rect(self.input_x, self.input_y, 380 - self.textfield_width, 50)
        self.proceed_button = [pygame.Rect((755, 479, 145, 62)), "Password Change"]
        self.x = 0
        self.x2 = 0  # Cursor position for input2
        self.open_overlay = False
        self.otp_start_time = None  # Initialized once
        self.input_1 = pygame.Rect(self.input_x, self.input_y, 380, 50)
        self.input_2 = pygame.Rect(self.input_x, self.input_y + 70, 380, 50)
        self.remaining = 60
        self.pw_mask = False
        self.verification = False
        self.error = ""
        self.error_label = font(20).render(self.error, True, (199, 0, 0))

    def container(self):
        self.overlay.fill((0, 0, 0, 130))
        self.screen.blit(self.overlay, (0, 0))
        pygame.draw.rect(self.screen, (69, 69, 69), ((self.screen.get_width() - 241 * self.scale) / 2,
                                                     (self.screen.get_height() - 151 * self.scale) / 2,
                                                     241 * self.scale,
                                                     151 * self.scale), border_radius=4)
        pygame.draw.rect(self.screen, (0, 131, 96), self.proceed_button[0], border_radius=4)
        proceed = font(20).render(self.proceed_txt, True, (255, 255, 255))
        self.screen.blit(proceed, (755 + (145 - proceed.get_width()) / 2, 479 + (62 - proceed.get_height()) / 2))

    def bar_shake(self, x=0, y=0):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_update_time >= 600:  # 10 FPS toggle
            self.frame_timer += 1
            self.last_update_time = current_time
            self.shake = not self.shake  # Toggle visibility

        # Calculate visible width based on masking
        if self.active_input == 1:
            visible_text = "*" * len(self.text) if self.pw_mask else self.text
            visible_width = self.font.size(visible_text)[0]
        else:
            visible_text = "*" * len(self.text2) if self.pw_mask else self.text2
            visible_width = self.font.size(visible_text)[0]

        # Update x to reflect where the blinking bar should be
        x = (self.input_1.x if self.active_input == 1 else self.input_2.x) + 10 + visible_width

        # Draw the blinking cursor
        if self.shake:
            pygame.draw.rect(self.screen, (255, 255, 255), (x, y, 3, 40))  # Visible
        else:
            pygame.draw.rect(self.screen, (0, 0, 0), (x, y, 3, 40))  # Hide (black)

    def handle_keydown(self, event):
        if self.active_input == 1:
            current_text = self.text
            x = self.x
        else:
            current_text = self.text2
            x = self.x2
        if event.key == pygame.K_BACKSPACE:
            if current_text:
                last_char_width = self.font.size(current_text[-1])[0]
                current_text = current_text[:-1]
                x -= last_char_width

        elif event.key == pygame.K_RETURN:
            print(f"Submitted: {current_text}")

        elif event.unicode.isalnum() and len(current_text) < self.max_length:
            current_text += event.unicode
            char_width = self.font.size(event.unicode)[0]
            x += char_width
        # Update the active field
        if self.active_input == 1:
            self.text = current_text
            self.x = x
        else:
            self.text2 = current_text
            self.x2 = x
        # Update the surface
        display_text = "*" * len(self.text) if self.pw_mask else self.text if self.text else self.placeholder
        color = pygame.Color('white') if self.text else pygame.Color('lightgray')
        self.txt_surface = self.font.render(display_text, True, color)

    def handle_click(self, mouse_pos):
        container_box = pygame.Rect(((self.screen.get_width() - 241 * self.scale) / 2,
                                     (self.screen.get_height() - 151 * self.scale) / 2,
                                     241 * self.scale,
                                     151 * self.scale))

        if not container_box.collidepoint(mouse_pos):
            self.open_overlay = False
            self.proceed_button[1] = "Password Change"
            self.textfield_width = 0
            self.input_rect = pygame.Rect(self.input_x, self.input_y, 380 - self.textfield_width, 50)
            self.otp_start_time = None
            self.clear()
            self.x = 0
            self.active_input = 1
        if self.proceed_button[0].collidepoint(mouse_pos):
            if self.proceed_button[1] == "Gmail":
                self.gmail = self.text
                print("Testing: ", self.gmail, bool(self.gmail))
                if not bool(self.gmail):
                    self.error = "Email cannot be empty"
                    self.error_label = font(20).render(self.error, True, (199, 0, 0))
                    print(self.error)
                else:
                    self.pin = otp(self.text + "@gmail.com")
                    print(self.pin)
                    print(self.text)
                    self.proceed_button[1] = "OTP"
                    self.clear()
                    self.x = 0
            elif self.proceed_button[1] == "OTP":
                if self.remaining == 0:
                    self.pin = None
                    print(self.pin)
                if self.pin:
                    if self.pin == self.text:
                        self.pw_mask = True
                        self.proceed_button[1] = "Change"
                        self.clear()
                        self.x = 0
                    else:
                        self.error = "Incorrect Pin"
                        self.error_label = font(20).render(self.error, True, (199, 0, 0))
            elif self.proceed_button[1] == "Change":
                try:
                    if not bool(self.text) and not bool(self.text2):
                        self.error = "Field is required"
                    elif self.text == self.text2:
                        print("Text: ", self.text)
                        pass_value = hash_password(self.text)
                        update_DB(f"UPDATE [Student] SET [Password] = '{pass_value}' WHERE "
                                  f"Email = "
                                  f"'{self.user_info[2].split('@')[0] if self.verification else self.gmail}@gmail.com'")
                        self.open_overlay = False
                    else:
                        self.error = "Password is not match"
                    self.error_label = font(20).render(self.error, True, (199, 0, 0))
                except Exception as e:
                    print("ErrorS: ", e)
            elif self.proceed_button[1] == "Password Change":
                userpass = select(f"Select Password from [Student] where StudentID = '{self.user_info[0]}'")[0][0]
                if not bool(self.text):
                    self.error = "Field is required"
                elif hash_password(self.text) == userpass:
                    self.proceed_button[1] = "Change"
                    self.verification = True
                    self.clear()
                    self.x = 0
                    return
                else:
                    self.error = "Incorrect Password"
                self.error_label = font(20).render(self.error, True, (199, 0, 0))
        elif self.proceed_button[1] == "OTP":
            # Check if OTP is being clicked
            try:
                otp_rect = pygame.Rect(400, 412, 70, 20)
                # This should match your blit position and approximate text size
                if otp_rect.collidepoint(mouse_pos):
                    self.pin = otp(self.gmail + "@gmail.com")
                    print(self.pin)
                    self.otp_start_time = pygame.time.get_ticks()
            except Exception as e:
                print("Error: ", e)
        elif self.proceed_button[1] == "Password Change":
            forgot_pass = pygame.Rect(400, 412, 185, 20)
            if forgot_pass.collidepoint(mouse_pos):
                self.active_input = 1
                self.pw_mask = True
                self.clear()
                self.input_rect = pygame.Rect(self.input_x, self.input_y, 380 - self.textfield_width, 50)
                self.x = 0
                self.proceed_button[1] = "Gmail"
                return
        if self.input_1.collidepoint(mouse_pos):
            self.active_input = 1
        elif self.input_2.collidepoint(mouse_pos):
            self.active_input = 2

    def _drawPw(self):
        self.container()
        self.proceed_txt = "Proceed"
        self.pw_mask = True
        self.proceed_button[1] = "Password Change"
        pygame.draw.rect(self.screen, (0, 0, 0), self.input_rect, border_radius=4)
        pygame.draw.rect(self.screen, (244, 244, 244), self.input_rect, width=3, border_radius=4)
        forgot_password = font(20).render("Forgot Password?", True, (255, 255, 255))
        self.screen.blit(self.error_label, (400, 372))
        self.screen.blit(forgot_password, (400, 412))
        self.screen.blit(self.txt_surface, (self.input_x + 10, self.input_y + 5))
        self.bar_shake(self.input_x + 10 + self.get_x(), self.input_y + 5)

    def _drawGmail(self):
        self.container()
        self.proceed_txt = "Proceed"
        self.pw_mask = False
        self.proceed_button[1] = "Gmail"
        gmail = font(20).render("@Gmail.com", True, (255, 255, 255))
        self.screen.blit(gmail, (783, 315))
        pygame.draw.rect(self.screen, (0, 0, 0), self.input_rect, border_radius=4)
        pygame.draw.rect(self.screen, (244, 244, 244), self.input_rect, width=3, border_radius=4)
        self.screen.blit(self.error_label, (400, 372))
        self.screen.blit(self.txt_surface, (self.input_x + 10, self.input_y + 5))
        self.bar_shake(self.input_x + 10 + self.get_x(), self.input_y + 5)

    def _drawOTP(self):
        self.container()
        self.proceed_txt = "Proceed"
        self.proceed_button[1] = "OTP"
        self.pw_mask = False
        self.textfield_width = 200
        self.input_rect = pygame.Rect(self.input_x, self.input_y, 380 - self.textfield_width, 50)
        if self.otp_start_time is None:
            self.otp_start_time = pygame.time.get_ticks()
        self.remaining = countdown(self.otp_start_time)  # Use stored start time
        self.Otp = font(20).render(f"OTP {self.remaining if self.remaining > 0 else 'Resend'}",
                                   True, (255, 255, 255))
        pygame.draw.rect(self.screen, (0, 0, 0), self.input_rect, border_radius=4)
        pygame.draw.rect(self.screen, (244, 244, 244), self.input_rect, width=3, border_radius=4)
        self.screen.blit(self.error_label, (400, 372))
        self.bar_shake(self.input_x + 10 + self.get_x(), self.input_y + 5)
        self.screen.blit(self.txt_surface, (self.input_x + 10, self.input_y + 5))
        self.screen.blit(self.Otp, (400, 412))

    def _drawChange(self):
        self.container()
        self.proceed_txt = "Done"
        self.pw_mask = True
        self.proceed_button[1] = "Change"
        # Draw input 1 (e.g., New Password)
        pygame.draw.rect(self.screen, (0, 0, 0), self.input_1, border_radius=4)
        pygame.draw.rect(self.screen, (244, 244, 244), self.input_1, width=3, border_radius=4)
        self.placeholder = "Password"
        display_text1 = "*" * len(self.text) if self.pw_mask and self.text else self.placeholder
        color1 = (255, 255, 255) if self.text else (200, 200, 200)
        txt_surface1 = self.font.render(display_text1, True, color1)
        # Draw cursor if active
        if self.active_input == 1:
            cursor_x = self.input_1.x + 10 + self.x
            self.bar_shake(cursor_x, self.input_1.y + 5)
        self.screen.blit(txt_surface1, (self.input_1.x + 10, self.input_1.y + 5))

        # Draw input 2 (e.g., Confirm Password)
        pygame.draw.rect(self.screen, (0, 0, 0), self.input_2, border_radius=4)
        pygame.draw.rect(self.screen, (244, 244, 244), self.input_2, width=3, border_radius=4)
        display_text2 = "*" * len(self.text2) if self.pw_mask and self.text2 else self.placeholder2
        color2 = (255, 255, 255) if self.text2 else (200, 200, 200)
        txt_surface2 = self.font.render(display_text2, True, color2)
        self.screen.blit(self.error_label, (400, 442))
        self.screen.blit(txt_surface2, (self.input_2.x + 10, self.input_2.y + 5))
        # Draw cursor if active
        if self.active_input == 2:
            cursor_x = self.input_2.x + 10 + self.x2
            self.bar_shake(cursor_x, self.input_2.y + 5)

    def get_value(self):
        return self.text

    def get_x(self):
        return self.x

    def page(self):
        if self.proceed_button[1] == "Password Change":
            return self._drawPw()
        elif self.proceed_button[1] == "Gmail":
            return self._drawGmail()
        elif self.proceed_button[1] == "OTP":
            return self._drawOTP()
        elif self.proceed_button[1] == "Change":
            self.pw_mask = True
            # self.bar_shake(self.input_x + 10 + self.get_x(), self.input_y + 5)
            return self._drawChange()

    def clear(self):
        self.placeholder = ""
        self.txt_surface = self.font.render(self.placeholder, True, (255, 255, 255))
        self.text = ""
        self.text2 = ""
        self.x2 = 0
        self.error = ""
        self.error_label = font(20).render(self.error, True, (199, 0, 0))
        self.x = 0


def load_image():
    with open("Red_Panda_Sprite_Sheet.json", "r") as file:
        return json.load(file)


class RedPanda:
    def __init__(self):
        self.panda_rect = None
        self.status = "Idle"
        self.prev_status = "Idle2"
        self.load = load_image()
        self.start_time = pygame.time.get_ticks()
        self.frames = []
        self.current_frame = 0
        self.last_update_time = pygame.time.get_ticks()
        self.loop = 6
        self.frame_duration = 130  # milliseconds per frame
        self.sprite_sheet = pygame.image.load(resource_path("Assets/Red Panda Sprite Sheet.png"))

    def load_frames(self):
        self.frames.clear()
        for i in range(self.loop):  # 6 idle frames
            frame_data = self.load["frames"][f"Red Panda Sprite Sheet ({self.get_status()}) {i}.ase"]["frame"]
            self.frames.append(frame_data)

    def _update(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time  # ✅ how long since reset
        if elapsed > 5000:
            self.set_status("Idle2")
            if elapsed > 6000:
                self.set_status("Idle")
                if elapsed > 7000:
                    self.loop = 8
                    self.set_status("Sleep")

        if self.get_status() != self.get_prev_status():
            self.set_prev_status(self.get_status())
            self.current_frame = 0
            self.load_frames()

        if now - self.last_update_time > self.frame_duration:
            self.last_update_time = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self, screen, position):
        self._update()
        frame = self.frames[self.current_frame]
        rect = pygame.Rect(frame["x"], frame["y"], frame["w"], frame["h"])
        image = self.sprite_sheet.subsurface(rect)
        scaled_image = pygame.transform.scale(image, (120, 120))
        screen.blit(scaled_image, position)

    def reset(self):
        self.start_time = pygame.time.get_ticks()
        self.set_status("Idle")
        self.set_prev_status("Idle2")  # Force load on next update
        self.loop = 6
        self.current_frame = 0
        self.load_frames()

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status

    def get_prev_status(self):
        return self.prev_status

    def set_prev_status(self, status):
        self.prev_status = status


class Background:
    def __init__(self, path, size=(1280, 800)):
        self.gif = Image.open(resource_path(path))
        self.frames = []
        self.size = size  # Desired output size

        try:
            while True:
                frame = self.gif.copy().convert("RGBA").resize(self.size)
                pygame_image = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
                self.frames.append(pygame_image)
                self.gif.seek(len(self.frames))  # Move to next frame
        except EOFError:
            pass

        self.frame_index = 0
        self.frame_duration = 100
        self.last_update = pygame.time.get_ticks()

    def play(self, screen):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)

        screen.blit(self.frames[self.frame_index], (0, 0))
