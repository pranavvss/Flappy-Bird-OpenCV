
Hand-Controlled Flappy Bird with OpenCV and MediaPipe
====================================================

This project is a fun implementation of a hand-controlled Flappy Bird game using Python, OpenCV, MediaPipe, and Pygame. The bird's vertical position is controlled using hand gestures detected via the webcam. The game includes a score counter and dynamic obstacle generation.




https://github.com/user-attachments/assets/dd09696b-c1bd-4deb-8c24-effa93a006c1


Requirements

---------------------------------------------------------------------

To run this project, you need the following dependencies installed:

- Python 3.x [Download Python latest version](https://www.python.org/downloads/)
- Pygame [Documentation on Pygame](https://pypi.org/project/pygame/)
- OpenCV [Documentation on OpenCV](https://opencv.org/releases/)
- MediaPipe [Documentation on Mediapipe](https://pypi.org/project/mediapipe/)

Installation

---------------------------------------------------------------------
You can install the required Python packages using pip:

```sh
pip install pygame opencv-python mediapipe
```

Code Breakdown

---------------------------------------------------------------------

### Importing Necessary Libraries

```python
import sys, time, random, pygame
from collections import deque
import cv2 as cv
import mediapipe as mp
```

- `sys`, `time`, `random`: Standard Python libraries for system operations, time management, and random number generation.
- `pygame`: A Python library used to create the game window and manage game elements.
- `collections.deque`: A double-ended queue to manage the obstacle pipes.
- `cv2 (OpenCV)`: A Python library for real-time computer vision, used to capture webcam input.
- `mediapipe`: A library for real-time hand tracking and gesture recognition.

---------------------------------------------------------------------

### Initializing Pygame and Setting Up the Game Window

```python
pygame.init()

desired_width = 640
desired_height = 480

window_size = (desired_width, desired_height)
screen = pygame.display.set_mode(window_size)
```

- `pygame.init()`: Initializes all the Pygame modules.
- `desired_width` and `desired_height`: Define the dimensions of the game window.
- `pygame.display.set_mode(window_size)`: Creates the game window with the specified size.

---------------------------------------------------------------------

### Video Capture Initialization

```python
VID_CAP = cv.VideoCapture(0)
```

- `cv.VideoCapture(0)`: Opens the webcam for video capture. `0` refers to the default webcam.
- 
---------------------------------------------------------------------

### Loading Bird and Pipe Images

```python
bird_img = pygame.image.load("bird_sprite.png")
bird_img = pygame.transform.scale(bird_img, (bird_img.get_width() // 6, bird_img.get_height() // 6))
bird_frame = bird_img.get_rect()
bird_frame.center = (window_size[0] // 6, window_size[1] // 2)
pipe_frames = deque()
pipe_img = pygame.image.load("pipe_sprite_single.png")
```

- `pygame.image.load()`: Loads the images for the bird and pipes.
- `pygame.transform.scale()`: Scales down the bird image.
- `bird_frame`: Defines the rectangle area occupied by the bird.
- `pipe_frames = deque()`: Initializes a deque to store and manage pipe obstacles.

---------------------------------------------------------------------

### Game Loop and Variables Initialization

```python
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
```

- Variables like `game_clock`, `stage`, `pipeSpawnTimer`, `time_between_pipe_spawn`, etc., are used to manage the timing, stage progression, and game state.
- `pipe_velocity`: A lambda function to calculate the velocity of the pipes based on the distance and time between spawns.

---------------------------------------------------------------------

### MediaPipe Hands Initialization

```python
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
```

- `mp_hands.Hands()`: Initializes the hand tracking model with parameters like `max_num_hands`, `min_detection_confidence`, and `min_tracking_confidence`.
- 
---------------------------------------------------------------------

### MediaPipe Drawing Utilities

```python
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
```

- `mp_drawing` and `mp_drawing_styles`: Used to draw hand landmarks and connections on the video feed.

---------------------------------------------------------------------

### Main Game Loop

```python
try:
    while True:
        if not game_is_running:
            text = pygame.font.SysFont("Helvetica Bold.ttf", 64).render('Game over!', True, (99, 245, 255))
            tr = text.get_rect()
            tr.center = (window_size[0] // 2, window_size[1] // 2)
            screen.blit(text, tr)
            pygame.display.update()
            pygame.time.wait(2000)
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_is_running = False
                break
```

- The main loop runs the game until `game_is_running` is `False`.
- If the game ends, it displays "Game over!" and waits for 2 seconds before exiting.

---------------------------------------------------------------------

### Capturing and Processing Webcam Frames

```python
ret, frame = VID_CAP.read()
if not ret:
    print("Empty frame, continuing...")
    continue
```

- `VID_CAP.read()`: Captures a frame from the webcam.
- If the frame is empty (failed capture), it prints a message and continues the loop.

---------------------------------------------------------------------

### Hand Detection and Bird Movement

```python
frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
results = hands.process(frame_rgb)

if results.multi_hand_landmarks:
    for hand_landmarks in results.multi_hand_landmarks:
        wrist_y = hand_landmarks.landmark[0].y
        bird_frame.centery = int((wrist_y - 0.5) * 1.5 * window_size[1] + window_size[1] / 2)
        if bird_frame.top < 0:
            bird_frame.y = 0
        if bird_frame.bottom > window_size[1]:
            bird_frame.y = window_size[1] - bird_frame.height

        mp_drawing.draw_landmarks(
            frame,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style()
        )
```

- Converts the frame to RGB for MediaPipe processing.
- `hands.process(frame_rgb)`: Detects hand landmarks.
- The bird's position (`bird_frame.centery`) is updated based on the y-coordinate of the wrist (`hand_landmarks.landmark[0].y`).
- Draws hand landmarks on the frame.

---------------------------------------------------------------------

### Drawing and Moving Pipes

```python
for pf in pipe_frames:
    pf[0].x -= pipe_velocity()
    pf[1].x -= pipe_velocity()

if len(pipe_frames) > 0 and pipe_frames[0][0].right < 0:
    pipe_frames.popleft()
```

- Moves the pipes from right to left.
- If the pipe moves out of the screen, it is removed from `pipe_frames`.

---------------------------------------------------------------------

### Blitting Frame to Pygame Surface

```python
frame = cv.flip(frame, 1).swapaxes(0, 1)
pygame.surfarray.blit_array(screen, frame)
screen.blit(bird_img, bird_frame)
```

- Flips the frame horizontally and swaps axes to match Pygame's coordinate system.
- Blits the frame to the Pygame window.

---------------------------------------------------------------------

### Score and Stage Update

```python
text = pygame.font.SysFont("Helvetica Bold.ttf", 50).render(f'Stage {stage}', True, (99, 245, 255))
tr = text.get_rect()
tr.center = (100, 50)
screen.blit(text, tr)
text = pygame.font.SysFont("Helvetica Bold.ttf", 50).render(f'Score: {score}', True, (99, 245, 255))
tr = text.get_rect()
tr.center = (100, 100)
screen.blit(text, tr)
pygame.display.flip()
```

- Displays the current stage and score at the top of the screen.

---------------------------------------------------------------------

### Clean Up Resources

```python
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    VID_CAP.release()
    cv.destroyAllWindows()
    pygame.quit()
    sys.exit()
```

- In case of an error, it prints the error message.
- Releases resources (camera, Pygame, OpenCV) and exits the program gracefully.

---------------------------------------------------------------------


