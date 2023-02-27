import pygame

# initialize Pygame
pygame.init()

# set the window size
window_size = (800, 600)

# create the Pygame window
screen = pygame.display.set_mode(window_size)

# set the window title
pygame.display.set_caption("Pong")

# set the clock for controlling the game's FPS
clock = pygame.time.Clock()

# set the colors
black = (0, 0, 0)
white = (255, 255, 255)

# create the fonts
font = pygame.font.Font(None, 36)

# create the sound effects
# pong_sound = pygame.mixer.Sound('pong.wav')
# score_sound = pygame.mixer.Sound('score.wav')

# set the initial velocities of the paddles and ball
paddle1_vel = 0
paddle2_vel = 0
ball_vel = [4, 4]
paddle_speed = 4

# set the sizes of the paddles and ball
paddle_width = 10
paddle_height = 100
ball_width = 10
ball_height = 10

# set the initial positions of the paddles and ball
paddle1_pos = [50, 250]
paddle2_pos = [750 - paddle_width, 250]
ball_pos = [400, 300]

# initialize the scores
score1 = 0
score2 = 0

# main game loop
running = True
while running:
    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        paddle2_vel = -paddle_speed
    elif keys[pygame.K_DOWN]:
        paddle2_vel = paddle_speed
    else:
        paddle2_vel = 0

    if keys[pygame.K_w]:
        paddle1_vel = -paddle_speed
    elif keys[pygame.K_s]:
        paddle1_vel = paddle_speed
    else:
        paddle1_vel = 0

    # update the positions of the paddles
    paddle1_pos[1] = max(min(paddle1_pos[1] + paddle1_vel, window_size[1] - paddle_height), 0)
    paddle2_pos[1] = max(min(paddle2_pos[1] + paddle2_vel, window_size[1] - paddle_height), 0)

    # update the game logic
    # update the position of the paddles based on their velocities
    # paddle1_pos[1] += paddle1_vel
    # paddle2_pos[1] += paddle2_vel

    # ensure that the paddles stay within the screen boundaries
    if paddle1_pos[1] < 0:
        paddle1_pos[1] = 0
    elif paddle1_pos[1] > window_size[1] - paddle_height:
        paddle1_pos[1] = window_size[1] - paddle_height

    if paddle2_pos[1] < 0:
        paddle2_pos[1] = 0
    elif paddle2_pos[1] > window_size[1] - paddle_height:
        paddle2_pos[1] = window_size[1] - paddle_height

    # update the position of the ball based on its velocity
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # check for collisions between the ball and the paddles
    if ball_pos[0] <= paddle_width + paddle1_pos[0]:
        if paddle1_pos[1] - ball_height <= ball_pos[1] <= paddle1_pos[1] + paddle_height and \
        ball_pos[0] >= paddle1_pos[0] + ball_width / 2:
            ball_vel[0] = -ball_vel[0]
            ball_pos[0] = paddle1_pos[0] + paddle_width
            print("1")

    elif ball_pos[0] >= window_size[0] - ball_width - (window_size[0] - paddle2_pos[0]):
        if paddle2_pos[1] - ball_height <= ball_pos[1] <= paddle2_pos[1] + paddle_height and \
        ball_pos[0] <= paddle2_pos[0] + paddle_width - ball_width / 2:
            ball_vel[0] = -ball_vel[0]
            ball_pos[0] = paddle2_pos[0] - paddle_width
            print("2")

    # check for collisions with the top and bottom of the screen
    if ball_pos[1] <= 0 or ball_pos[1] >= window_size[1] - ball_height:
        ball_vel[1] = -ball_vel[1]

    # check for collisions with the left and right sides of the screen
    if ball_pos[0] < 0:
        ball_pos = [300, 200]
        ball_vel = [4, 4]
        score2 += 1
    elif ball_pos[0] > window_size[0] - ball_width:
        ball_pos = [300, 200]
        ball_vel = [-4, -4]
        score1 += 1

    # update the velocity of the ball based on the paddle's velocity
    # ball_vel[0] += 0.1 * ball_vel[0] * abs(paddle1_vel + paddle2_vel) / 20
    # ball_vel[1] += 0.1 * ball_vel[1] * abs(paddle1_vel + paddle2_vel) / 20

    # clear the screen
    screen.fill(black)

    # draw the paddles and ball
    pygame.draw.rect(screen, white, [paddle1_pos[0], paddle1_pos[1], paddle_width, paddle_height])
    pygame.draw.rect(screen, white, [paddle2_pos[0], paddle2_pos[1], paddle_width, paddle_height])
    pygame.draw.rect(screen, white, [ball_pos[0], ball_pos[1], ball_width, ball_height])

    # draw the score
    score_text = font.render(str(score1) + " - " + str(score2), True, white)
    screen.blit(score_text, [window_size[0] // 2 - score_text.get_width() // 2, 10])

    # update the display
    pygame.display.update()

    # control the game's FPS
    clock.tick(60)

# quit Pygame
pygame.quit()