import math
import random
import pygame

# define global colors
# BLACK = (0, 0, 0)
# WHITE = (255, 255, 255)

# define global game parameters
# BALL_SPEED_INCREASE = 25
# PADDLE_SPEED = 350

class Ball:
    def __init__(self, x, y, width, height, color, vel, window_width, window_height, speed_increase):
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
        self.speed_increase = speed_increase

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

class Paddle:
    def __init__(self, x, y, width, height, color, left):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.left = left
        self.vel = 0
        self.hits = 0

    def move(self, window_height, dt):
        self.y = max(min(self.y + self.vel / (1000 / dt),
                     window_height - self.height), 0)

    def bounce_ball_if_collision(self, ball):
        if self.left:
            if ball.x <= self.x + self.width and ball.prev_x > self.x + self.width:
                t, intersect_y = calculate_interpolation(
                    ball.prev_x, ball.x, ball.prev_y, ball.y, self.x + self.width)
                if self.check_collision_y(ball, intersect_y):
                    bounce_angle = self.calculate_bounce_angle(intersect_y)
                    self.adjust_ball_velocity(ball, bounce_angle)
                    ball.x = self.x + ball.width
                    ball.y = intersect_y
                    self.hits += 1
        else:
            if ball.x + ball.width >= self.x and ball.prev_x + ball.width < self.x:
                t, intersect_y = calculate_interpolation(
                    ball.prev_x + ball.width, ball.x + ball.width, ball.prev_y, ball.y, self.x)
                if self.check_collision_y(ball, intersect_y):
                    bounce_angle = self.calculate_bounce_angle(
                        intersect_y)
                    self.adjust_ball_velocity(ball, bounce_angle)
                    ball.x = self.x - ball.width
                    ball.y = intersect_y
                    self.hits += 1

    def check_collision_y(self, ball, intersect_y):
        return self.y - ball.height <= intersect_y <= self.y + self.height + ball.height

    def calculate_bounce_angle(self, intersect_y):
        relative_intersect_y = (self.y + self.height / 2) - intersect_y
        normalized_intersect_y = relative_intersect_y / (self.height / 2)
        bounce_angle = normalized_intersect_y * math.pi / 3
        return bounce_angle

    def adjust_ball_velocity(self, ball, bounce_angle):
        ball.vel[0] = abs(ball.vel[0]) + ball.speed_increase if self.left else -abs(ball.vel[0]) - ball.speed_increase
        ball.vel[1] = -ball.vel[0] * math.sin(bounce_angle) if self.left else ball.vel[0] * math.sin(bounce_angle)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, pygame.Rect(
            round(self.x), round(self.y), self.width, self.height))
        
class GodPaddle(Paddle):
    def __init__(self, x, y, width, height, color, left):
        super().__init__(x, y, width, height, color, left)
        
    def move(self, *args):
        pass

    def calculate_bounce_angle(self, intersect_y):
        # Calculate a random angle for the ball's bounce
        bounce_angle = random.uniform(-math.pi/3, math.pi/3)
        return bounce_angle

    def draw(self, *args):
        super().draw(*args)


class Game:

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BALL_SPEED_INCREASE = 25
    PADDLE_SPEED = 350
    MAX_SCORE = 3

    def __init__(self, window_width=800, window_height=600, render=True, player1: Paddle=None, player2: Paddle=None, vsync=True):
        pygame.display.set_caption("Pong")
        self.window_width = window_width
        self.window_height = window_height
        self.screen = pygame.display.set_mode(
            (self.window_width, self.window_height), flags=pygame.SCALED, vsync=vsync) if render else None
        self.render_clock = pygame.time.Clock()
        self.logic_clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        # initialize paddles and ball
        if player1 is None:
            self.paddle1 = Paddle(50, 250, 10, 100, self.WHITE, True)
        else:
            self.paddle1 = player1
        if player2 is None:
            self.paddle2 = Paddle(750 - 10, 250, 10, 100, self.WHITE, False)
        else:
            self.paddle2 = player2

        self.ball = Ball(400, 300, 10, 10, self.WHITE, [
                         175, 175], window_width, window_height, self.BALL_SPEED_INCREASE)
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
        text_surface = self.font.render(score_text, True, self.WHITE)
        text_rect = text_surface.get_rect(center=(self.window_width/2, 50))
        self.screen.blit(text_surface, text_rect)

    def run_one_frame(self, bot_input=None, dt=1000/60, render=False, tickrate=60):
        '''
        Runs the game loop with a constant update step until the user quits the game.
        Can take paddle movement input as an optional argument (for AI control).
        returns false if user quits the game, true otherwise
        '''
        try:
            self.logic_clock.tick(tickrate)
            # blocks until enough time has passed time for the next logic tick
            if not self.handle_events():
                self.done = True
                return False
            # input is 1 for up, 2 for down, 0 for no input
            if bot_input is not None:
                self.paddle1.vel = -self.PADDLE_SPEED if bot_input == 1 else self.PADDLE_SPEED if bot_input == 2 else 0
            self.update_game_logic(dt)  # passes a constant dt value
            if self.check_game_over():
                return False

            if render:
                self.screen.fill(self.BLACK)
                self.draw_objects()
                # pygame.display.update()
                pygame.display.flip()

            return True
        except:
            print("stopping in game loop due to exception!")
            self.done = True
            return False

    def run(self, tickrate=60, render_fps=60):
        '''Runs the game loop with decoupled tickrate and fps until the user quits the game'''
        last_render_time = pygame.time.get_ticks()
        while not self.done:
            # Update game state
            # print("updating game logic")
            dt = self.logic_clock.tick(tickrate)
            # print("logic tick dt: ", dt, "ms")
            if not self.handle_events():
                break
            self.update_game_logic(dt)
            self.check_game_over()

            # Render the frame
            if pygame.time.get_ticks() - last_render_time >= 1000 / render_fps:
                # print("rendering frame")
                # print("frametime: ", pygame.time.get_ticks() - last_render_time, "ms")
                last_render_time = pygame.time.get_ticks()
                self.screen.fill(self.BLACK)
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
        self.paddle2.vel = -self.PADDLE_SPEED if keys[pygame.K_UP] else self.PADDLE_SPEED if keys[pygame.K_DOWN] else 0
        self.paddle1.vel = -self.PADDLE_SPEED if keys[pygame.K_w] else self.PADDLE_SPEED if keys[pygame.K_s] else 0

        return True

    def update_game_logic(self, dt):
        self.move_paddles(dt)
        self.move_ball(dt)
        self.paddle1.bounce_ball_if_collision(self.ball)
        self.paddle2.bounce_ball_if_collision(self.ball)
        self.check_collision_with_walls()
        self.check_ball_off_screen()

    def move_paddles(self, dt):
        self.paddle1.move(self.window_height, dt)
        self.paddle2.move(self.window_height, dt)

    def move_ball(self, dt):
        self.ball.move(dt)
    
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
        
    def check_game_over(self):
        if self.score1 >= self.MAX_SCORE or self.score2 >= self.MAX_SCORE:
            self.done = True
            return True
        return False

    def get_game_state(self):
        return [self.ball.x, self.ball.y, self.ball.vel[0], self.ball.vel[1], \
                    self.paddle1.y, self.paddle2.y]
        
    def get_scaled_game_state(self):
        # seems bugged. maybe because of int division instead of floats?
        return [self.ball.x / 800, self.ball.y / 600, self.ball.vel[0] / 300, self.ball.vel[1] / 300, \
                    self.paddle1.y / 600, self.paddle2.y / 600]


def calculate_interpolation(x1, x2, y1, y2, target_x):
    t = (target_x - x1) / (x2 - x1)
    intersect_y = y1 + (y2 - y1) * t
    return t, intersect_y


if __name__ == '__main__':
    pygame.init()
    window_size = (800, 600)
    game = Game(*window_size, render=True, player2=GodPaddle(750 - 10, 0, 10, 600, Game.WHITE, False))
    while game.run_one_frame(bot_input=None, dt=1000/60, render=True, tickrate=60):
        # print(game.get_game_data())
        pass
