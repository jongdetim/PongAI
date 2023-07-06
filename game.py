import math
import pygame

# define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

BALL_SPEED_INCREASE = 25
PADDLE_SPEED = 350

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
    
    # BLACK = (0, 0, 0)
    # WHITE = (255, 255, 255)
    # BALL_SPEED_INCREASE = 25
    # PADDLE_SPEED = 350

    def __init__(self, window_width=800, window_height=600, logic_fps=120, render_fps=60):
        self.window_width = window_width
        self.window_height = window_height
        self.logic_fps = logic_fps
        self.render_fps = render_fps
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        self.render_clock = pygame.time.Clock()
        self.logic_clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.paddle1 = Paddle(50, 250, 10, 100, WHITE)
        self.paddle2 = Paddle(750 - 10, 250, 10, 100, WHITE)
        self.ball = Ball(400, 300, 10, 10, WHITE, [175, 175], window_width, window_height)
        self.score1 = 0
        self.score2 = 0
        self.done = False

    def draw_objects(self):
        # Draw paddles and ball
        self.ball.draw(self.screen)
        self.paddle1.draw(self.screen)
        self.paddle2.draw(self.screen)

        # Draw scores
        score_text = f"{self.score1} - {self.score2}"
        text_surface = self.font.render(score_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.window_width/2, 50))
        self.screen.blit(text_surface, text_rect)

    def run_one_frame(self, input=None, dt=1000/60, render=False):
        '''
        Runs the game loop with a constant update step until the user quits the game.
        Can take paddle movement input as an optional argument (for AI control).
        returns false if user quits the game, true otherwise
        '''
        self.logic_clock.tick(self.logic_fps)
        if not self.handle_events():
            return False
        # have to change this to the neat model output.
        if input is not None:
            self.paddle2.vel = -PADDLE_SPEED if input[0] else PADDLE_SPEED if input[1] else 0
            self.paddle1.vel = -PADDLE_SPEED if input[2] else PADDLE_SPEED if input[3] else 0
        self.update_game_logic(dt) # passes a constant dt value

        if render:
            self.screen.fill(BLACK)
            self.draw_objects()
            pygame.display.update()
            
        return True
      
    def run(self):
        '''Runs the game loop with decoupled tickrate and fps until the user quits the game'''
        last_render_time = pygame.time.get_ticks()
        while True:
            # Update game state
            # print("updating game logic")
            dt = self.logic_clock.tick(self.logic_fps)
            # print("logic tick dt: ", dt, "ms")
            if not self.handle_events():
                break
            self.update_game_logic(dt)
            
            # Render the frame
            if pygame.time.get_ticks() - last_render_time >= 1000 / self.render_fps:
                # print("rendering frame")
                # print("frametime: ", pygame.time.get_ticks() - last_render_time, "ms")
                last_render_time = pygame.time.get_ticks()
                self.screen.fill(BLACK)
                self.draw_objects()
                pygame.display.update()

            # Pause briefly to slow down the game loop
            # print("frametime: ", self.clock.tick(self.fps))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

        keys = pygame.key.get_pressed()
        # Changes paddle velocity if key is pressed
        self.paddle2.vel = -PADDLE_SPEED if keys[pygame.K_UP] else PADDLE_SPEED if keys[pygame.K_DOWN] else 0
        self.paddle1.vel = -PADDLE_SPEED if keys[pygame.K_w] else PADDLE_SPEED if keys[pygame.K_s] else 0

        return True

    def update_game_logic(self, dt):
        self.move_paddles(dt)
        self.move_ball(dt)
        self.check_collision_with_paddle1()
        self.check_collision_with_paddle2()
        self.check_collision_with_walls()
        self.check_ball_off_screen()

    def move_paddles(self, dt):
        self.paddle1.move(self.window_height, dt)
        self.paddle2.move(self.window_height, dt)

    def move_ball(self, dt):
        self.ball.move(dt)

    def check_collision_with_paddle1(self):
        if self.ball.x <= self.paddle1.x + self.ball.width and self.ball.prev_x > self.paddle1.x + self.ball.width:
            t, intersect_y = self.calculate_interpolation(self.ball.prev_x, self.ball.x, self.ball.prev_y, self.ball.y, self.paddle1.x + self.paddle1.width)
            if self.check_collision_y(intersect_y, self.paddle1):
                bounce_angle = self.calculate_bounce_angle(intersect_y, self.paddle1)
                self.adjust_ball_velocity(self.paddle1, bounce_angle)
                self.ball.x = self.paddle1.x + self.paddle1.width
                self.ball.y = intersect_y

    def check_collision_with_paddle2(self):
        if self.ball.x + self.ball.width >= self.paddle2.x and self.ball.prev_x + self.ball.width < self.paddle2.x:
            t, intersect_y = self.calculate_interpolation(self.ball.prev_x + self.ball.width, self.ball.x + self.ball.width, self.ball.prev_y, self.ball.y, self.paddle2.x)
            if self.check_collision_y(intersect_y, self.paddle2):
                bounce_angle = self.calculate_bounce_angle(intersect_y, self.paddle2)
                self.adjust_ball_velocity(self.paddle2, bounce_angle)
                self.ball.x = self.paddle2.x - self.ball.width
                self.ball.y = intersect_y

    def calculate_interpolation(self, x1, x2, y1, y2, target_x):
        t = (target_x - x1) / (x2 - x1)
        intersect_y = y1 + (y2 - y1) * t
        return t, intersect_y

    def check_collision_y(self, intersect_y, paddle):
        return paddle.y - self.ball.height <= intersect_y <= paddle.y + paddle.height + self.ball.height

    def calculate_bounce_angle(self, intersect_y, paddle):
        relative_intersect_y = (paddle.y + paddle.height / 2) - intersect_y
        normalized_intersect_y = relative_intersect_y / (paddle.height / 2)
        bounce_angle = normalized_intersect_y * math.pi / 3
        return bounce_angle

    def adjust_ball_velocity(self, paddle, bounce_angle):
        if paddle is self.paddle1:
            self.ball.vel[0] = abs(self.ball.vel[0]) + BALL_SPEED_INCREASE
            self.ball.vel[1] = -self.ball.vel[0] * math.sin(bounce_angle)
        else:
            self.ball.vel[0] = -abs(self.ball.vel[0]) - BALL_SPEED_INCREASE
            self.ball.vel[1] = self.ball.vel[0] * math.sin(bounce_angle)

    def check_collision_with_walls(self):
        if self.ball.y <= 0:
            self.ball.vel[1] *= -1
            self.ball.y = 0
        elif self.ball.y + self.ball.height >= self.window_height:
            self.ball.vel[1] *= -1
            self.ball.y = self.window_height - self.ball.height

    def check_ball_off_screen(self):
        if self.ball.x < -self.ball.width:
            self.score2 += 1
            self.ball.reset_position(1)
        elif self.ball.x > self.window_width:
            self.score1 += 1
            self.ball.reset_position(-1)
            
    def get_game_data(self):
        ball_position = (self.ball.x, self.ball.y)
        paddles_y_position = (self.paddle1.y, self.paddle2.y)
        ball_velocity = tuple(self.ball.vel)
        score = (self.score1, self.score2)
        # should probably return a dictionary for the neat algorithm
        return ball_position, paddles_y_position, ball_velocity, score


if __name__ == '__main__':
    # initialize Pygame
    pygame.init()

    # set the window size and fps
    window_size = (800, 600)
    logic_fps = 60
    render_fps = 60

    # create the Pygame window
    # flags = pygame.OPENGL
    screen = pygame.display.set_mode(window_size, flags=pygame.SCALED, vsync=1)
    # screen = pygame.display.set_mode(window_size)

    # set the window title
    pygame.display.set_caption("Pong")

    game = Game(*window_size, logic_fps, render_fps)
    # game.run()
    while game.run_one_frame(dt=1000/60, render=True):
        print(game.get_game_data())
