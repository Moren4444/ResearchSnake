import pygame


class Snake:
    def __init__(self, x, y, scale):
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

        # Initialize snake positions
        self.positions = [(x - i * (self.body_width * scale), y * scale) for i in range(self.body_count)]

        # Load sprites
        self._load_sprites()

    def _load_sprites(self):
        """Load all required sprites for the snake"""
        self.head_sprites = {
            "up": self._load_sprite("assets/Snakes/head_up.png"),
            "down": self._load_sprite("assets/Snakes/head_down.png"),
            "left": self._load_sprite("assets/Snakes/head_left.png"),
            "right": self._load_sprite("assets/Snakes/head_right.png"),
        }

        self.tail_sprites = {
            "up": self._load_sprite("assets/Snakes/tail_up.png"),
            "down": self._load_sprite("assets/Snakes/tail_down.png"),
            "left": self._load_sprite("assets/Snakes/tail_left.png"),
            "right": self._load_sprite("assets/Snakes/tail_right.png"),
        }

        self.body_horizontal = self._load_sprite("assets/Snakes/body_horizontal.png")
        self.body_vertical = self._load_sprite("assets/Snakes/body_vertical.png")

        self.turn_sprites = {
            "topleft": self._load_sprite("assets/Snakes/body_topleft.png"),
            "topright": self._load_sprite("assets/Snakes/body_topright.png"),
            "bottomleft": self._load_sprite("assets/Snakes/body_bottomleft.png"),
            "bottomright": self._load_sprite("assets/Snakes/body_bottomright.png"),
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
    def __init__(self, x, y, screen, scale):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.snake = Snake(x, y, scale)

    def _getPosition(self):
        return self.snake.getPosition()

    def _animated_text(self, sentence, font, x, y, space_between, max_width, animation_speed=50):
        # Create unique identifier for each text instance
        text_key = (sentence, x, y)  # Unique combination of content and position

        # Initialize animation state if not exists
        if not hasattr(self, '_anim_states'):
            self._anim_states = {}

        if text_key not in self._anim_states:
            self._anim_states[text_key] = {
                'index': 0,
                'lines': [],
                'current_line': '',
                'current_line_width': 0,
                'current_word': '',
                'current_word_width': 0,
                'last_update_time': pygame.time.get_ticks(),
                'animation_speed': animation_speed  # Use parameter value
            }

        state = self._anim_states[text_key]
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - state['last_update_time']

        # Calculate how many characters to process based on animation speed
        chars_to_process = max(1, int(elapsed_time / state['animation_speed']))

        if chars_to_process > 0:
            state['last_update_time'] = current_time

            for _ in range(chars_to_process):
                if state['index'] >= len(sentence):
                    break

                char = sentence[state['index']]
                state['index'] += 1
                char_width = font.size(char)[0]

                # Existing word wrapping logic
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

        # Draw existing lines
        current_y = y
        for line in state['lines']:
            text_surf = font.render(line, True, (0, 0, 0))
            self.screen.blit(text_surf, (x + space_between, current_y + space_between))
            current_y += text_surf.get_height() + space_between

        # Draw current line + current word
        current_text = state['current_line'] + (
            ' ' + state['current_word'] if state['current_line'] else state['current_word'])
        text_surf = font.render(current_text, True, (0, 0, 0))
        self.screen.blit(text_surf, (x + space_between, current_y + space_between))

        return state['index'] >= len(sentence)

    def _update(self, scale, body_count, dead):
        """Update game state"""
        keys = pygame.key.get_pressed()
        self.snake.handle_input(keys)
        self.snake.update(scale, body_count, dead)  # Pass body_count to update

    def _draw(self, scale):
        """Draw game elements"""
        self.snake.draw(self.screen, scale)
