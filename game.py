import math
import pygame

# define colors
black = (0, 0, 0)
white = (255, 255, 255)

BALL_SPEED_INCREASE = 25

class Paddle:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.vel = 0

    def move(self, window_height, dt):
        self.y = max(min(self.y + self.vel / (1000 / dt), window_height - self.height), 0)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, pygame.Rect(
            round(self.x), round(self.y), self.width, self.height))


class Ball:
    def __init__(self, x, y, width, height, color, vel, window_width, window_height):
        self.x = x
        self.prev_x = x
        self.y = y
        self.prev_y = y
        self.width = width
        self.height = height
        self.color = color
        self.vel = vel
        self.window_width = window_width
        self.window_height = window_height

    def move(self, dt):
        self.prev_x = self.x
        self.prev_y = self.y
        self.x += self.vel[0] / (1000 / dt)
        self.y += self.vel[1] / (1000 / dt)

    def reset_position(self, sign):
        self.x = self.window_width // 2
        self.y = self.window_height // 2
        self.vel = [sign * 175, sign * 175]

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, pygame.Rect(
            round(self.x), round(self.y), self.width, self.height))


class Game:
    def __init__(self, window_width=800, window_height=600, logic_fps=120, render_fps=60):
        self.window_width = window_width
        self.window_height = window_height
        self.logic_fps = logic_fps
        self.render_fps = render_fps
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        self.render_clock = pygame.time.Clock()
        self.logic_clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.paddle1 = Paddle(50, 250, 10, 100, white)
        self.paddle2 = Paddle(750 - 10, 250, 10, 100, white)
        self.ball = Ball(400, 300, 10, 10, white, [175, 175], window_width, window_height)
        self.score1 = 0
        self.score2 = 0

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

    # def run(self):
    #     while self.handle_events():
    #         # Update game state
    #         self.logic_clock.tick(self.logic_fps)
    #         self.update_game_logic()

    #         # Draw the updated game state to the screen
    #         self.render_clock.tick(self.render_fps)
    #         self.screen.fill(black)
    #         self.draw_objects()
    #         pygame.display.update()

    #         # Pause briefly to slow down the game loop
    #         # print("frametime: ", self.clock.tick(self.fps))
            
    def run_decoupled_fps(self):
        last_render_time = pygame.time.get_ticks()
        while True:
            # Update game state
            # print("updating game logic")
            dt = self.logic_clock.tick(self.logic_fps)
            # print("logic tick dt: ", dt, "ms")
            if not self.handle_events(dt):
                break
            self.update_game_logic(dt)
            
            # Render the frame
            if pygame.time.get_ticks() - last_render_time >= 1000 / self.render_fps:
                # print("rendering frame")
                # print("frametime: ", pygame.time.get_ticks() - last_render_time, "ms")
                last_render_time = pygame.time.get_ticks()
                self.screen.fill(black)
                self.draw_objects()
                pygame.display.update()

            # Pause briefly to slow down the game loop
            # print("frametime: ", self.clock.tick(self.fps))

    def handle_events(self, dt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

        keys = pygame.key.get_pressed()
        self.paddle2.vel = -350 if keys[pygame.K_UP] else 350 if keys[pygame.K_DOWN] else 0
        self.paddle1.vel = -350 if keys[pygame.K_w] else 350 if keys[pygame.K_s] else 0

        return True

    def update_game_logic(self, dt):
        # Move the paddles
        self.paddle1.move(self.window_height, dt)
        self.paddle2.move(self.window_height, dt)

        # Move the ball
        self.ball.move(dt)

        # Check collision with left paddle using linear interpolation
        if self.ball.x <= self.paddle1.x + self.ball.width and self.ball.prev_x > self.paddle1.x + self.ball.width:
            t = (self.paddle1.x + self.paddle1.width - self.ball.prev_x) / (self.ball.x - self.ball.prev_x)
            intersect_y = self.ball.prev_y + (self.ball.y - self.ball.prev_y) * t
            if self.paddle1.y - self.ball.height <= intersect_y <= self.paddle1.y + self.paddle1.height + self.ball.height:
                # Calculate the angle of impact
                relative_intersect_y = (self.paddle1.y + self.paddle1.height / 2) - intersect_y
                normalized_intersect_y = relative_intersect_y / (self.paddle1.height / 2)
                bounce_angle = normalized_intersect_y * math.pi / 3
                # Adjust the velocity of the ball based on the angle of impact
                self.ball.vel[0] = abs(self.ball.vel[0]) + BALL_SPEED_INCREASE
                self.ball.vel[1] = -self.ball.vel[0] * math.sin(bounce_angle)
                self.ball.x = self.paddle1.x + self.paddle1.width
                self.ball.y = intersect_y



        # Check collision with right paddle using linear interpolation
        if self.ball.x + self.ball.width >= self.paddle2.x and self.ball.prev_x + self.ball.width < self.paddle2.x:
            t = (self.paddle2.x - self.ball.prev_x - self.ball.width) / (self.ball.x - self.ball.prev_x)
            intersect_y = self.ball.prev_y + (self.ball.y - self.ball.prev_y) * t
            if self.paddle2.y - self.ball.height <= intersect_y <= self.paddle2.y + self.paddle2.height + self.ball.height:
                # Calculate the angle of impact
                relative_intersect_y = (self.paddle2.y + self.paddle2.height / 2) - intersect_y
                normalized_intersect_y = relative_intersect_y / (self.paddle2.height / 2)
                bounce_angle = normalized_intersect_y * math.pi / 3
                # Adjust the velocity of the ball based on the angle of impact
                self.ball.vel[0] = -abs(self.ball.vel[0]) - BALL_SPEED_INCREASE
                self.ball.vel[1] = self.ball.vel[0] * math.sin(bounce_angle)
                self.ball.x = self.paddle2.x - self.ball.width
                self.ball.y = intersect_y




        # Check collision with top/bottom walls
        if self.ball.y <= 0:
            self.ball.vel[1] *= -1
            self.ball.y = 0
            
        elif self.ball.y + self.ball.height >= self.window_height:
            self.ball.vel[1] *= -1
            self.ball.y = self.window_height - self.ball.height

        # Check if the ball has gone off the left or right edge of the screen
        if self.ball.x < -self.ball.width:
            self.score2 += 1
            self.ball.reset_position(1)
        elif self.ball.x > self.window_width:
            self.score1 += 1
            self.ball.reset_position(-1)


if __name__ == '__main__':
    # initialize Pygame
    pygame.init()

    # set the window size and fps
    window_size = (800, 600)
    logic_fps = 1000
    render_fps = 60

    # create the Pygame window
    flags = pygame.OPENGL
    screen = pygame.display.set_mode(window_size, flags=pygame.SCALED, vsync=1)
    # screen = pygame.display.set_mode(window_size)

    # set the window title
    pygame.display.set_caption("Pong")

    game = Game(*window_size, logic_fps, render_fps)
    game.run_decoupled_fps()
