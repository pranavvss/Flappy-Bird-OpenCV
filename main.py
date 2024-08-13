import sys, time, random, pygame
from collections import deque
import cv2 as cv
import mediapipe as mp

# Initialize required elements/environment
pygame.init()
VID_CAP = cv.VideoCapture(0)
window_size = (int(VID_CAP.get(cv.CAP_PROP_FRAME_WIDTH)), int(VID_CAP.get(cv.CAP_PROP_FRAME_HEIGHT)))
screen = pygame.display.set_mode(window_size)

# Bird and pipe init
bird_img = pygame.image.load("bird_sprite.png")
bird_img = pygame.transform.scale(bird_img, (bird_img.get_width() // 6, bird_img.get_height() // 6))
bird_frame = bird_img.get_rect()
bird_frame.center = (window_size[0] // 6, window_size[1] // 2)
pipe_frames = deque()
pipe_img = pygame.image.load("pipe_sprite_single.png")

pipe_starting_template = pipe_img.get_rect()
space_between_pipes = 250

# Game loop
game_clock = time.time()
stage = 1
pipeSpawnTimer = 0
time_between_pipe_spawn = 40
dist_between_pipes = 500
pipe_velocity = lambda: dist_between_pipes / time_between_pipe_spawn
level = 0
score = 0
didUpdateScore = False
game_is_running = True

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Initialize MediaPipe Drawing for Hand Skeleton
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

while True:
    # Check if game is running
    if not game_is_running:
        text = pygame.font.SysFont("Helvetica Bold.ttf", 64).render('Game over!', True, (99, 245, 255))
        tr = text.get_rect()
        tr.center = (window_size[0] // 2, window_size[1] // 2)
        screen.blit(text, tr)
        pygame.display.update()
        pygame.time.wait(2000)
        VID_CAP.release()
        cv.destroyAllWindows()
        pygame.quit()
        sys.exit()

    # Check if user quit window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            VID_CAP.release()
            cv.destroyAllWindows()
            pygame.quit()
            sys.exit()

    # Get frame
    ret, frame = VID_CAP.read()
    if not ret:
        print("Empty frame, continuing...")
        continue

    # Clear screen
    screen.fill((125, 220, 232))

    # Hand detection
    frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Get the y-coordinate of the wrist (landmark 0)
            wrist_y = hand_landmarks.landmark[0].y
            bird_frame.centery = int((wrist_y - 0.5) * 1.5 * window_size[1] + window_size[1] / 2)
            if bird_frame.top < 0:
                bird_frame.y = 0
            if bird_frame.bottom > window_size[1]:
                bird_frame.y = window_size[1] - bird_frame.height

            # Draw hand landmarks and connections on the right hand
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

    # Mirror frame, swap axes because opencv != pygame
    frame = cv.flip(frame, 1).swapaxes(0, 1)

    # Update pipe positions
    for pf in pipe_frames:
        pf[0].x -= pipe_velocity()
        pf[1].x -= pipe_velocity()

    if len(pipe_frames) > 0 and pipe_frames[0][0].right < 0:
        pipe_frames.popleft()

    # Update screen
    pygame.surfarray.blit_array(screen, frame)
    screen.blit(bird_img, bird_frame)
    checker = True
    for pf in pipe_frames:
        # Check if bird went through to update score
        if pf[0].left <= bird_frame.x <= pf[0].right:
            checker = False
            if not didUpdateScore:
                score += 1
                didUpdateScore = True
        # Update screen
        screen.blit(pipe_img, pf[1])
        screen.blit(pygame.transform.flip(pipe_img, 0, 1), pf[0])
    if checker:
        didUpdateScore = False

    # Stage, score text
    text = pygame.font.SysFont("Helvetica Bold.ttf", 50).render(f'Stage {stage}', True, (99, 245, 255))
    tr = text.get_rect()
    tr.center = (100, 50)
    screen.blit(text, tr)
    text = pygame.font.SysFont("Helvetica Bold.ttf", 50).render(f'Score: {score}', True, (99, 245, 255))
    tr = text.get_rect()
    tr.center = (100, 100)
    screen.blit(text, tr)

    # Update screen
    pygame.display.flip()

    # Check if bird is touching a pipe
    if any([bird_frame.colliderect(pf[0]) or bird_frame.colliderect(pf[1]) for pf in pipe_frames]):
        game_is_running = False

    # Time to add new pipes
    if pipeSpawnTimer == 0:
        top = pipe_starting_template.copy()
        top.x, top.y = window_size[0], random.randint(120 - 1000, window_size[1] - 120 - space_between_pipes - 1000)
        bottom = pipe_starting_template.copy()
        bottom.x, bottom.y = window_size[0], top.y + 1000 + space_between_pipes
        pipe_frames.append([top, bottom])

    # Update pipe spawn timer - make it cyclical
    pipeSpawnTimer += 1
    if pipeSpawnTimer >= time_between_pipe_spawn:
        pipeSpawnTimer = 0

    # Update stage
    if time.time() - game_clock >= 10:
        time_between_pipe_spawn *= 5 / 6
        stage += 1
        game_clock = time.time()
