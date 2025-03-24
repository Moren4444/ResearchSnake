import pygame
import random


class Option:
    def __init__(self, resource_path):
        # Load button images
        self.blue_A = pygame.image.load(resource_path("assets/MV_Icons_Letter_Buttons/Buttons/blue-A.png"))
        self.blue_A_push = pygame.image.load(resource_path("assets/MV_Icons_Letter_Buttons/Buttons/blue-A-pushed.png"))

        self.green_B = pygame.image.load(resource_path("assets/MV_Icons_Letter_Buttons/Buttons/green-B.png"))
        self.green_B_push = pygame.image.load(resource_path("assets/MV_Icons_Letter_Buttons/Buttons/green-B-pushed.png"))

        self.red_C = pygame.image.load(resource_path("assets/MV_Icons_Letter_Buttons/Buttons/red-C.png"))
        self.red_C_push = pygame.image.load(resource_path("assets/MV_Icons_Letter_Buttons/Buttons/red-C-pushed.png"))

        self.yellow_D = pygame.image.load(resource_path("assets/MV_Icons_Letter_Buttons/Buttons/yellow-D.png"))
        self.yellow_D_push = pygame.image.load(resource_path("assets/MV_Icons_Letter_Buttons/Buttons/yellow-D-pushed.png"))

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

        self.frame_duration = 1  # Number of seconds to display each frame
        self.frame_timer = 0  # Tracks time since last frame switch
        self.current_state = "normal"  # Tracks whether buttons are in normal or pushed state

    def update(self, dt):
        """Update the animation state."""
        self.frame_timer += dt / 1000  # Convert milliseconds to seconds
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
        """Reset button positions to new random coordinates."""
        for button in self.buttons:
            button["x"] = random.randrange(680, 1020, 40)
            button["y"] = random.randrange(92, 692, 40)


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


def main():
    # Initialize Pygame
    pygame.init()

    # Screen setup
    screen = pygame.display.set_mode((1280, 800))
    clock = pygame.time.Clock()

    # Create an Option object
    option = Option()

    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Update and draw the option
        option.update(clock.get_time())
        option.draw(screen)

        # Cap the frame rate at 3 FPS
        clock.tick(3)

    # Quit Pygame
    pygame.quit()


if __name__ == "__main__":
    main()
