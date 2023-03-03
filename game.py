import pygame


class Paddle:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.vel = 0

    def move(self, window_height):
        self.y = max(min(self.y + self.vel, window_height - self.height), 0)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, pygame.Rect(
            self.x, self.y, self.width, self.height))


class Ball:
    def __init__(self, x, y, width, height, color, vel, window_width, window_height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.vel = vel
        self.window_width = window_width
        self.window_height = window_height

    def move(self):
        self.x += int(self.vel[0])
        self.y += int(self.vel[1])

    def reset_position(self, sign):
        self.x = self.window_width // 2
        self.y = self.window_height // 2
        self.vel = [sign *4, sign * 4]

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, pygame.Rect(
            self.x, self.y, self.width, self.height))


class Game:
    def __init__(self, window_width=800, window_height=600, fps=60):
        self.window_width = window_width
        self.window_height = window_height
        self.fps = fps
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.paddle1 = Paddle(50, 250, 10, 100, white)
        self.paddle2 = Paddle(750 - 10, 250, 10, 100, white)
        self.ball = Ball(400, 300, 10, 10, white, [4, 4], window_width, window_height)
        self.score1 = 0
        self.score2 = 0
        self.game_over = False

    def draw_objects(self):
        # Draw paddles and ball
        self.ball.draw(self.screen)
        self.paddle1.draw(self.screen)
        self.paddle2.draw(self.screen)

        # Draw scores
        score_text = f"{self.score1} - {self.score2}"
        text_surface = self.font.render(score_text, True, white)
        text_rect = text_surface.get_rect(center=(self.window_width/2, 50))
        self.screen.blit(text_surface, text_rect)

    def run(self):
        while not self.game_over:
            # Handle events (user input)
            if not self.handle_events():
                break

            # Update game state
            self.update_game_logic()

            # Draw the updated game state to the screen
            self.screen.fill(black)
            self.draw_objects()
            pygame.display.update()

            # Pause briefly to slow down the game loop
            self.clock.tick(self.fps)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

        keys = pygame.key.get_pressed()
        self.paddle2.vel = - 4 if keys[pygame.K_UP] else 4 if keys[pygame.K_DOWN] else 0
        self.paddle1.vel = - 4 if keys[pygame.K_w] else 4 if keys[pygame.K_s] else 0

        return True

    def update_game_logic(self):
        self.paddle1.move(self.window_height)
        self.paddle2.move(self.window_height)
        self.ball.move()

        # Check collision with left paddle
        if self.ball.x <= self.paddle1.x + self.paddle1.width:
            if self.paddle1.y - self.ball.height <= self.ball.y <= self.paddle1.y + self.paddle1.height and self.ball.x >= self.paddle1.x + self.paddle1.width // 2:
                self.ball.vel[0] = -self.ball.vel[0] + 0.5
                self.ball.x = self.paddle1.x + self.paddle2.width

        # Check collision with right paddle
        if self.ball.x + self.ball.width >= self.paddle2.x:
            if self.paddle2.y - self.ball.height <= self.ball.y <= self.paddle2.y + self.paddle2.height and self.ball.x <= self.paddle2.x + self.paddle2.width // 2:
                self.ball.vel[0] = -self.ball.vel[0] - 0.5
                self.ball.x = self.paddle2.x - self.paddle2.width

        # Check collision with top/bottom walls
        if self.ball.y <= self.ball.height/2 or self.ball.y + self.ball.height/2 >= self.window_height:
            self.ball.vel[1] = -self.ball.vel[1]

        # Check if ball goes past left/right walls
        if self.ball.x <= 0:
            self.score2 += 1
            self.ball.reset_position(1)
        elif self.ball.x + self.ball.width >= self.window_width:
            self.score1 += 1
            self.ball.reset_position(-1)


if __name__ == '__main__':
    # initialize Pygame
    pygame.init()

    # set the window size
    window_size = (800, 600)

    # create the Pygame window
    screen = pygame.display.set_mode(window_size)

    # set the colors
    black = (0, 0, 0)
    white = (255, 255, 255)

    # set the window title
    pygame.display.set_caption("Pong")

    game = Game()
    game.run()
