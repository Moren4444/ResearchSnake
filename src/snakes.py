import pygame


class Snake:
    def __init__(self, x, y, scale, resource_path):
        self.frame_width = 40
        self.frame_height = 40
        self.direction = "right"
        self.body_width = self.frame_width
        self.body_height = self.frame_height
        self.body_count = 3  # Default body count
        self.snake_can_move = True
        self.scale = scale
        self.turn_points = {}
        self.new_head = []

        self.resource_path = resource_path

        # Initialize snake positions
        self.positions = [(x - i * (self.body_width * scale), y * scale) for i in range(self.body_count)]

        # Load sprites
        self._load_sprites()

    def _load_sprites(self):
        """Load all required sprites for the snake"""
        self.head_sprites = {
            "up": self._load_sprite(self.resource_path("assets/Snakes/head_up.png")),
            "down": self._load_sprite(self.resource_path("assets/Snakes/head_down.png")),
            "left": self._load_sprite(self.resource_path("assets/Snakes/head_left.png")),
            "right": self._load_sprite(self.resource_path("assets/Snakes/head_right.png")),
        }

        self.tail_sprites = {
            "up": self._load_sprite(self.resource_path("assets/Snakes/tail_up.png")),
            "down": self._load_sprite(self.resource_path("assets/Snakes/tail_down.png")),
            "left": self._load_sprite(self.resource_path("assets/Snakes/tail_left.png")),
            "right": self._load_sprite(self.resource_path("assets/Snakes/tail_right.png")),
        }

        self.body_horizontal = self._load_sprite(self.resource_path("assets/Snakes/body_horizontal.png"))
        self.body_vertical = self._load_sprite(self.resource_path("assets/Snakes/body_vertical.png"))

        self.turn_sprites = {
            "topleft": self._load_sprite(self.resource_path("assets/Snakes/body_topleft.png")),
            "topright": self._load_sprite(self.resource_path("assets/Snakes/body_topright.png")),
            "bottomleft": self._load_sprite(self.resource_path("assets/Snakes/body_bottomleft.png")),
            "bottomright": self._load_sprite(self.resource_path("assets/Snakes/body_bottomright.png")),
        }

    def _load_sprite(self, path):
        """Helper method to load and subsurface a sprite"""
        return pygame.image.load(path).subsurface((0, 0, self.frame_width, self.frame_height))

    def get_turn_type(self, prev_dir, new_dir):
        """Determine the turn sprite type based on direction change"""
        turn_map = {
            ("up", "left"): "bottomleft",
            ("up", "right"): "bottomright",
            ("down", "left"): "topleft",
            ("down", "right"): "topright",
            ("left", "up"): "topright",
            ("left", "down"): "bottomright",
            ("right", "up"): "topleft",
            ("right", "down"): "bottomleft",
        }
        return turn_map.get((prev_dir, new_dir), None)

    def get_tail_direction(self, tail, body):
        """Determine tail direction based on adjacent body segment"""
        if tail[0] < body[0]: return "left"
        if tail[0] > body[0]: return "right"
        if tail[1] < body[1]: return "up"
        return "down"

    def handle_input(self, keys):
        """Handle keyboard input for direction changes"""
        if not self.snake_can_move:
            return

        prev_direction = self.direction
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.direction != "down":
            self.direction = "up"
        elif (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.direction != "up":
            self.direction = "down"
        elif (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.direction != "right":
            self.direction = "left"
        elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.direction != "left":
            self.direction = "right"

        # Record turn point if direction changed
        if prev_direction != self.direction:
            turn_type = self.get_turn_type(prev_direction, self.direction)
            if turn_type:
                self.turn_points[tuple(self.positions[0])] = (turn_type, self.direction)

    def _resize_body(self, positions, new_body_count):
        """Resize the snake's body to match the new body count"""
        if new_body_count > len(positions):
            # Add new body segments
            for _ in range(new_body_count - len(positions)):
                positions.append(positions[-1])
        elif new_body_count < len(positions):
            # Remove extra body segments
            positions = positions[:new_body_count]
        return positions

    def update(self, scale, body_count, dead):
        """Update snake position and check collisions"""
        if not self.snake_can_move:
            return

        # Update body count if it has changed
        if body_count != self.body_count:
            self.body_count = body_count
            self.positions = self._resize_body(self.positions, body_count)
        if dead != self.snake_can_move:
            self.snake_can_move = dead

        # Calculate new head position
        self.new_head = list(self.positions[0])
        if self.direction == "up":
            self.new_head[1] -= self.body_height * scale
        elif self.direction == "down":
            self.new_head[1] += self.body_height * scale
        elif self.direction == "left":
            self.new_head[0] -= self.body_width * scale
        elif self.direction == "right":
            self.new_head[0] += self.body_width * scale

        # Check collision
        new_head_tuple = tuple(self.new_head)
        if new_head_tuple in self.positions[1:-1]:
            self.snake_can_move = False

        # Update positions
        self.positions.insert(0, new_head_tuple)
        old_tail = self.positions.pop()
        if old_tail in self.turn_points:
            del self.turn_points[old_tail]

    def draw(self, surface, scale):
        """Draw the snake on the specified surface"""
        # Draw head
        scaled_head = pygame.transform.scale(self.head_sprites[self.direction], (40 * scale, 40 * scale))
        scaled_body_h = pygame.transform.scale(self.body_horizontal, (40 * scale, 40 * scale))
        scaled_body_v = pygame.transform.scale(self.body_vertical, (40 * scale, 40 * scale))

        surface.blit(scaled_head, self.positions[0])

        # Draw body
        for i in range(1, len(self.positions) - 1):
            current_pos = self.positions[i]
            if current_pos in self.turn_points:
                turn_type, _ = self.turn_points[current_pos]
                scaled_turn = pygame.transform.scale(self.turn_sprites[turn_type], (40 * scale, 40 * scale))
                surface.blit(scaled_turn, current_pos)
            else:
                prev_pos = self.positions[i - 1]
                next_pos = self.positions[i + 1]
                if prev_pos[0] == next_pos[0]:
                    surface.blit(scaled_body_v, current_pos)
                elif prev_pos[1] == next_pos[1]:
                    surface.blit(scaled_body_h, current_pos)

        # Draw tail
        tail_pos = self.positions[-1]
        body_pos = self.positions[-2]
        tail_dir = self.get_tail_direction(tail_pos, body_pos)
        scaled_tail = pygame.transform.scale(self.tail_sprites[tail_dir], (40 * scale, 40 * scale))
        surface.blit(scaled_tail, tail_pos)

    def getPosition(self):
        return self.new_head


class Game:
    def __init__(self, x, y, screen, scale, duration, resource_path, difficulties):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.snake = Snake(x, y, scale, resource_path)
        self.time_bar_start = pygame.time.get_ticks()
        self.time_bar_duration = duration  # 10 seconds in milliseconds
        self.full_width = 250 * 2  # Initial width from your code
        self.paused = False
        self.last_move_time = pygame.time.get_ticks()
        self.move_interval = difficulties
        self.pause_start_time = 0
        self.timer_started = False

    def pause(self):
        """Pause the timer."""
        if not self.paused:
            self.paused = True
            self.pause_start_time = pygame.time.get_ticks()

    def resume(self):
        """Resume the timer and adjust for paused time."""
        if self.paused:
            self.paused = False
            pause_duration = pygame.time.get_ticks() - self.pause_start_time
            self.time_bar_start += pause_duration  # Adjust start time

    def _getPosition(self):
        return self.snake.getPosition()

    def _TimeBar(self):
        if self.paused:
            # Use the time when paused to calculate remaining time
            current_time = self.pause_start_time
        else:
            current_time = pygame.time.get_ticks()

        elapsed = current_time - self.time_bar_start
        remaining = max(0, self.time_bar_duration - elapsed)
        width = (remaining / self.time_bar_duration) * self.full_width

        # Color logic remains the same
        if remaining < 2000:
            color = (255, 0, 0)
        else:
            color = (16, 196, 109)

        pygame.draw.rect(self.screen, color, (29 * 2, 27 * 2, width, 10.85 * 2),
                         border_top_left_radius=5, border_top_right_radius=5)

        # Return whether time has run out
        return remaining <= 0

    def _animated_text(self, sentence, font, x, y, space_between, max_width, char_rate=20):
        """Animate text appearance at a constant speed (characters per second)."""
        text_key = (sentence, x, y)

        # Initialize animation state if it doesn't exist
        if not hasattr(self, '_anim_states'):
            self._anim_states = {}
        if text_key not in self._anim_states:
            self._anim_states[text_key] = {
                'start_time': pygame.time.get_ticks(),
                'lines': [],
                'current_line': '',
                'current_line_width': 0,
                'current_word': '',
                'current_word_width': 0,
                'completed': False
            }

        state = self._anim_states[text_key]
        elapsed = pygame.time.get_ticks() - state['start_time']

        # Determine how many characters should be visible based on a constant rate.
        visible_chars = int((elapsed / 1000.0) * char_rate)
        visible_chars = min(visible_chars, len(sentence))  # Do not exceed total text length

        # Only reprocess if animation is not completed
        if not state['completed']:
            visible_text = sentence[:visible_chars]

            # Reset state for reprocessing the visible text
            state['lines'] = []
            state['current_line'] = ''
            state['current_line_width'] = 0
            state['current_word'] = ''
            state['current_word_width'] = 0

            # Process each character in the visible text
            for char in visible_text:
                char_width = font.size(char)[0]

                if char == ' ':
                    potential_width = state['current_line_width'] + state['current_word_width'] + char_width
                    if potential_width > max_width:
                        state['lines'].append(state['current_line'])
                        state['current_line'] = state['current_word'] + ' '
                        state['current_line_width'] = state['current_word_width'] + char_width
                    else:
                        state['current_line'] += state['current_word'] + ' '
                        state['current_line_width'] += state['current_word_width'] + char_width
                    state['current_word'] = ''
                    state['current_word_width'] = 0
                else:
                    new_word = state['current_word'] + char
                    new_word_width = font.size(new_word)[0]
                    potential_width = state['current_line_width'] + (
                        font.size(' ')[0] if state['current_line'] else 0) + new_word_width

                    if potential_width > max_width:
                        if state['current_line']:
                            state['lines'].append(state['current_line'])
                        state['current_line'] = new_word
                        state['current_line_width'] = new_word_width
                        state['current_word'] = ''
                        state['current_word_width'] = 0
                    else:
                        state['current_word'] = new_word
                        state['current_word_width'] = new_word_width

            # If we have displayed all characters, mark as completed.
            if visible_chars == len(sentence):
                state['completed'] = True

        # Draw all complete lines
        current_y = y
        for line in state['lines']:
            text_surf = font.render(line, True, (0, 0, 0))
            self.screen.blit(text_surf, (x + space_between, current_y + space_between))
            current_y += text_surf.get_height() + space_between

        # Draw the current line (including the word in progress)
        current_text = state['current_line'] + (
            ' ' + state['current_word'] if state['current_line'] else state['current_word'])
        if current_text.strip():
            text_surf = font.render(current_text, True, (0, 0, 0))
            self.screen.blit(text_surf, (x + space_between, current_y + space_between))

        return state['completed']

    def _update(self, scale, body_count, dead):
        """Update game state"""
        keys = pygame.key.get_pressed()

        # self.snake.update(scale, body_count, dead)  # Pass body_count to update
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time >= self.move_interval:
            self.snake.handle_input(keys)
            self.snake.update(scale, body_count, dead)
            self.last_move_time = current_time

    def _draw(self, scale):
        """Draw game elements"""
        self.snake.draw(self.screen, scale)
