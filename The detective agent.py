

import pygame
import random
import math
import array
import sys

# ==========================================================
# THE DEDUCTIVE GAME - VERSION 4.0
# SPECIAL HINT EDITION
# ==========================================================

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("THE DEDUCTIVE GAME - Case Files")
clock = pygame.time.Clock()

# ---------------- FONTS ----------------

FONT = pygame.font.SysFont("arial", 17, bold=True)
SMALL = pygame.font.SysFont("arial", 13)
MEDIUM = pygame.font.SysFont("arial", 23, bold=True)
BIG = pygame.font.SysFont("arial", 43, bold=True)
TITLE = pygame.font.SysFont("arial", 53, bold=True)

# ---------------- COLOURS ----------------

WHITE = (245, 247, 255)
GOLD = (255, 195, 85)
CYAN = (70, 220, 240)
BLUE = (55, 125, 220)
RED = (235, 75, 90)
GREEN = (75, 220, 150)
BLACK = (8, 10, 20)

# ---------------- AUDIO ----------------

try:
    pygame.mixer.init()
    AUDIO = True
except pygame.error:
    AUDIO = False


def create_sound(freq, duration=0.1, volume=0.15):
    if not AUDIO:
        return None

    rate = 22050
    count = int(rate * duration)
    data = array.array("h")

    for i in range(count):
        fade = 1 - i / count
        wave = math.sin(2 * math.pi * freq * i / rate)
        data.append(
            int(32767 * volume * fade * wave)
        )

    try:
        return pygame.mixer.Sound(buffer=data.tobytes())
    except pygame.error:
        return None


CLICK = create_sound(650)
WRONG = create_sound(180, 0.16)
FOUND = create_sound(900, 0.22)
WIN_SOUND = create_sound(1050, 0.4)


def play(sound):
    if sound:
        sound.play()


# ==========================================================
# GAME DATA
# ==========================================================

scene = "home"

suspects = [
    {
        "name": "AVA MORGAN",
        "job": "The Hacker",
        "colour": (105, 65, 125)
    },
    {
        "name": "BRUNO REED",
        "job": "The Driver",
        "colour": (55, 100, 145)
    },
    {
        "name": "CYRUS VALE",
        "job": "The Mastermind",
        "colour": (145, 65, 75)
    }
]

secret_code = ""
criminal_index = 0

guess = ""
attempts = 10
wrong_attempts = 0

feedback = "Enter your first three-digit guess."

# Permanent hint history
hints = []

# Current displayed hint
current_hint = "No special hints unlocked yet."

history = []


# ==========================================================
# NEW CASE AND HINT RESET
# ==========================================================

def new_case():
    global secret_code, criminal_index
    global guess, attempts, wrong_attempts
    global feedback, hints, current_hint, history

    secret_code = "".join(
        random.sample("123456789", 3)
    )

    criminal_index = (
        sum(int(digit) for digit in secret_code) % 3
    )

    guess = ""
    attempts = 10
    wrong_attempts = 0

    feedback = "Enter your first three-digit guess."

    hints = []
    history = []

    current_hint = "No special hints unlocked yet."


new_case()


# ==========================================================
# ANIMATIONS
# ==========================================================

rain = [
    [
        random.randrange(WIDTH),
        random.randrange(HEIGHT),
        random.randrange(5, 12)
    ]
    for _ in range(150)
]

cars = [
    {
        "x": -150,
        "y": 390,
        "speed": 2.5,
        "colour": (45, 100, 170)
    },
    {
        "x": 850,
        "y": 420,
        "speed": 1.7,
        "colour": (145, 55, 75)
    }
]

stars = [
    (random.randrange(WIDTH), random.randrange(270))
    for _ in range(65)
]


# ==========================================================
# DRAWING HELPERS
# ==========================================================

def text(value, x, y, colour=WHITE, font=FONT):
    image = font.render(str(value), True, colour)
    screen.blit(image, (int(x), int(y)))


def centered(value, y, colour=WHITE, font=FONT):
    image = font.render(str(value), True, colour)
    screen.blit(
        image,
        image.get_rect(center=(WIDTH // 2, y))
    )


def panel(rect, colour, border=None, radius=12):
    pygame.draw.rect(
        screen, colour, rect, border_radius=radius
    )

    if border:
        pygame.draw.rect(
            screen, border, rect, 2,
            border_radius=radius
        )


def button(rect, label, colour=BLUE):
    hover = rect.collidepoint(pygame.mouse.get_pos())

    if hover:
        colour = tuple(
            min(255, c + 25) for c in colour
        )

    panel(
        rect,
        (12, 19, 38),
        colour,
        10
    )

    image = FONT.render(label, True, WHITE)

    screen.blit(
        image,
        image.get_rect(center=rect.center)
    )


def gradient(top, bottom):
    for y in range(HEIGHT):
        t = y / HEIGHT

        colour = tuple(
            int(top[i] * (1-t) + bottom[i] * t)
            for i in range(3)
        )

        pygame.draw.line(
            screen, colour,
            (0, y), (WIDTH, y)
        )


def glow(x, y, radius, colour):
    for r in range(radius, 0, -10):

        layer = pygame.Surface(
            (r*2, r*2),
            pygame.SRCALPHA
        )

        alpha = int(20*r/radius)

        pygame.draw.circle(
            layer,
            (*colour, alpha),
            (r, r),
            r
        )

        screen.blit(layer, (x-r, y-r))


# ==========================================================
# RAIN
# ==========================================================

def update_rain():
    for drop in rain:

        drop[0] += 1.2
        drop[1] += drop[2]

        if drop[1] > HEIGHT:
            drop[0] = random.randrange(WIDTH)
            drop[1] = random.randrange(-80, -5)


def draw_rain():
    for x, y, speed in rain:

        pygame.draw.line(
            screen,
            (105, 155, 195),
            (int(x), int(y)),
            (int(x-3), int(y+speed*2)),
            1
        )


# ==========================================================
# CITY BACKGROUND
# ==========================================================

def draw_lamp(x, bottom):

    glow(x, 170, 80, (255, 185, 85))

    pygame.draw.line(
        screen,
        (22, 27, 40),
        (x, bottom),
        (x, 145),
        7
    )

    pygame.draw.line(
        screen,
        (22, 27, 40),
        (x, 145),
        (x+25, 135),
        6
    )

    pygame.draw.circle(
        screen, GOLD, (x+25, 135), 9
    )

    pygame.draw.circle(
        screen, WHITE, (x+25, 135), 3
    )


def draw_city():

    gradient(
        (8, 15, 42),
        (48, 35, 72)
    )

    # Stars

    for x, y in stars:
        pygame.draw.circle(
            screen,
            (130, 145, 180),
            (x, y),
            1
        )

    # Moon

    glow(790, 85, 75, (105, 145, 255))

    pygame.draw.circle(
        screen,
        (220, 225, 245),
        (790, 85),
        27
    )

    # Buildings

    buildings = [
        (0, 115, 205),
        (120, 135, 285),
        (260, 120, 220),
        (385, 145, 320),
        (535, 130, 235),
        (670, 125, 290),
        (800, 120, 205)
    ]

    for bx, bw, bh in buildings:

        pygame.draw.rect(
            screen,
            (22, 31, 59),
            (bx, 380-bh, bw, bh)
        )

        pygame.draw.rect(
            screen,
            (35, 43, 72),
            (bx+6, 385-bh, bw-12, bh-5)
        )

        for wy in range(380-bh+18, 365, 35):

            for wx in range(bx+14, bx+bw-10, 25):

                if (wx*3 + wy*7) % 5:

                    pygame.draw.rect(
                        screen,
                        (210, 165, 100),
                        (wx, wy, 9, 14)
                    )

                else:

                    pygame.draw.rect(
                        screen,
                        (45, 65, 95),
                        (wx, wy, 9, 14)
                    )

    # Road

    pygame.draw.rect(
        screen,
        (35, 36, 51),
        (0, 380, WIDTH, 220)
    )

    pygame.draw.rect(
        screen,
        (85, 75, 82),
        (0, 378, WIDTH, 7)
    )

    # Road markings

    for x in range(-60, WIDTH, 160):

        pygame.draw.rect(
            screen,
            (190, 175, 130),
            (x, 520, 75, 4)
        )

    # Wet road reflections

    for i in range(25):

        x = (
            i*51 + pygame.time.get_ticks()//20
        ) % WIDTH

        y = 540 + (i*9 % 50)

        pygame.draw.line(
            screen,
            (75, 95, 130),
            (x, y),
            (x+20, y-2),
            2
        )

    draw_lamp(65, 350)
    draw_lamp(830, 340)

    draw_rain()


# ==========================================================
# MOVING CARS WITH ROTATING WHEELS
# ==========================================================

def draw_car(car):

    x = int(car["x"])
    y = car["y"]
    colour = car["colour"]

    pygame.draw.ellipse(
        screen,
        BLACK,
        (x-5, y+27, 135, 17)
    )

    pygame.draw.rect(
        screen,
        colour,
        (x, y, 125, 34),
        border_radius=11
    )

    pygame.draw.polygon(
        screen,
        colour,
        [
            (x+23, y),
            (x+44, y-24),
            (x+94, y-24),
            (x+111, y)
        ]
    )

    pygame.draw.polygon(
        screen,
        (120, 180, 205),
        [
            (x+49, y-19),
            (x+91, y-19),
            (x+103, y-3),
            (x+37, y-3)
        ]
    )

    angle = pygame.time.get_ticks()/70

    for wx in (x+27, x+99):

        pygame.draw.circle(
            screen, BLACK, (wx, y+31), 13
        )

        pygame.draw.circle(
            screen, (145, 155, 175),
            (wx, y+31), 7
        )

        for a in range(0, 360, 90):

            rad = math.radians(a+angle)

            ex = wx + math.cos(rad)*6
            ey = y+31 + math.sin(rad)*6

            pygame.draw.line(
                screen,
                (50, 55, 65),
                (wx, y+31),
                (int(ex), int(ey)),
                2
            )

    pygame.draw.circle(
        screen, GOLD, (x+122, y+13), 5
    )

    glow(x+122, y+13, 25, (255, 210, 110))


def update_cars():

    for car in cars:

        car["x"] += car["speed"]

        if car["x"] > WIDTH+150:

            car["x"] = -160

            car["y"] = random.choice(
                [390, 420]
            )


# ==========================================================
# DETECTIVE CHARACTER
# ==========================================================

def draw_detective(x, base, moving=False):

    t = pygame.time.get_ticks()/100

    swing = math.sin(t)*13 if moving else 0
    arm = math.sin(t+math.pi)*9 if moving else 0
    bob = abs(math.sin(t))*3 if moving else 0

    x = int(x)
    y = base-bob

    pygame.draw.ellipse(
        screen,
        BLACK,
        (x-34, base-5, 68, 13)
    )

    # Legs

    pygame.draw.line(
        screen, (27, 30, 45),
        (x-10, y-63),
        (x-12-swing, y-8), 11
    )

    pygame.draw.line(
        screen, (27, 30, 45),
        (x+10, y-63),
        (x+12+swing, y-8), 11
    )

    # Shoes

    pygame.draw.ellipse(
        screen, (8, 9, 16),
        (x-34-swing, y-15, 29, 12)
    )

    pygame.draw.ellipse(
        screen, (8, 9, 16),
        (x+8+swing, y-15, 29, 12)
    )

    # Coat

    pygame.draw.polygon(
        screen, (35, 45, 72),
        [
            (x-22, y-145),
            (x+22, y-145),
            (x+34, y-54),
            (x+13, y-45),
            (x, y-59),
            (x-15, y-45),
            (x-34, y-54)
        ]
    )

    pygame.draw.polygon(
        screen, (72, 82, 112),
        [
            (x-22, y-145),
            (x, y-119),
            (x-11, y-90)
        ]
    )

    pygame.draw.polygon(
        screen, (72, 82, 112),
        [
            (x+22, y-145),
            (x, y-119),
            (x+11, y-90)
        ]
    )

    for by in range(4):

        pygame.draw.circle(
            screen, GOLD,
            (x, int(y-110+by*15)), 2
        )

    # Arms

    pygame.draw.line(
        screen, (35, 45, 72),
        (x-19, y-135),
        (x-29+arm, y-83), 12
    )

    pygame.draw.line(
        screen, (35, 45, 72),
        (x+19, y-135),
        (x+29-arm, y-83), 12
    )

    pygame.draw.circle(
        screen, (220, 165, 130),
        (int(x-29+arm), int(y-82)), 7
    )

    pygame.draw.circle(
        screen, (220, 165, 130),
        (int(x+29-arm), int(y-82)), 7
    )

    # Neck

    pygame.draw.rect(
        screen, (190, 135, 110),
        (x-7, y-161, 14, 20)
    )

    # Face

    pygame.draw.ellipse(
        screen, (226, 178, 145),
        (x-19, y-198, 38, 43)
    )

    pygame.draw.circle(
        screen, (205, 145, 115),
        (x-19, y-176), 6
    )

    pygame.draw.circle(
        screen, (205, 145, 115),
        (x+19, y-176), 6
    )

    # Hat

    pygame.draw.rect(
        screen, (23, 27, 42),
        (x-21, y-210, 42, 17),
        border_radius=5
    )

    pygame.draw.ellipse(
        screen, (15, 20, 33),
        (x-28, y-198, 56, 9)
    )

    pygame.draw.line(
        screen, GOLD,
        (x-15, y-194),
        (x+15, y-194), 3
    )

    # Eyes

    pygame.draw.circle(
        screen, BLACK, (x-7, int(y-177)), 2
    )

    pygame.draw.circle(
        screen, BLACK, (x+7, int(y-177)), 2
    )

    pygame.draw.line(
        screen, (150, 90, 75),
        (x, y-173),
        (x+2, y-166), 2
    )

    pygame.draw.line(
        screen, (120, 65, 65),
        (x-4, y-159),
        (x+4, y-159), 2
    )


# ==========================================================
# SUSPECT PORTRAITS
# ==========================================================

def draw_suspect(index, rect, revealed=False):

    suspect = suspects[index]

    x, y, w, h = rect

    border = RED if revealed else GOLD

    panel(
        pygame.Rect(x, y, w, h),
        (12, 20, 42),
        border,
        12
    )

    # Portrait background

    pygame.draw.circle(
        screen,
        suspect["colour"],
        (x+w//2, y+49),
        31
    )

    # Face

    pygame.draw.ellipse(
        screen,
        (222, 170, 135),
        (x+w//2-15, y+30, 30, 38)
    )

    # Hair

    pygame.draw.arc(
        screen,
        (35, 25, 24),
        (x+w//2-16, y+25, 32, 25),
        math.pi, 2*math.pi, 7
    )

    # Eyes

    pygame.draw.circle(
        screen, BLACK,
        (x+w//2-6, y+45), 2
    )

    pygame.draw.circle(
        screen, BLACK,
        (x+w//2+6, y+45), 2
    )

    # Clothing

    if index == 1:

        pygame.draw.line(
            screen, (35, 30, 38),
            (x+w//2-14, y+51),
            (x+w//2+14, y+51), 6
        )

    pygame.draw.polygon(
        screen,
        suspect["colour"],
        [
            (x+w//2-18, y+82),
            (x+w//2+18, y+82),
            (x+w//2+27, y+105),
            (x+w//2-27, y+105)
        ]
    )

    name_image = SMALL.render(
        suspect["name"], True, WHITE
    )

    screen.blit(
        name_image,
        name_image.get_rect(
            center=(x+w//2, y+120)
        )
    )

    job_image = SMALL.render(
        suspect["job"], True, CYAN
    )

    screen.blit(
        job_image,
        job_image.get_rect(
            center=(x+w//2, y+140)
        )
    )

    if revealed:

        label = MEDIUM.render(
            "CRIMINAL!", True, RED
        )

        screen.blit(
            label,
            label.get_rect(
                center=(x+w//2, y+h-15)
            )
        )


# ==========================================================
# SPECIAL HINT SYSTEM - NEW IN VERSION 4.0
# ==========================================================

def give_hint():

    global current_hint

    # HINT 1: After 3 incorrect attempts
    if wrong_attempts == 3:

        digit = secret_code[0]

        current_hint = (
            "HINT 1: The secret code contains the digit "
            + digit + ". Position unknown!"
        )

        hints.append(current_hint)

        play(FOUND)

    # HINT 2: After 6 incorrect attempts
    elif wrong_attempts == 6:

        middle_digit = int(secret_code[1])

        if middle_digit % 2 == 0:
            kind = "EVEN"
        else:
            kind = "ODD"

        current_hint = (
            "HINT 2: The MIDDLE digit is " + kind + "."
        )

        hints.append(current_hint)

        play(FOUND)

    # HINT 3: After 9 incorrect attempts
    elif wrong_attempts == 9:

        last_digit = secret_code[2]

        current_hint = (
            "HINT 3: The LAST digit is "
            + last_digit + "!"
        )

        hints.append(current_hint)

        play(FOUND)


# ==========================================================
# MAIN GAME SCREEN
# ==========================================================

def game_screen():

    draw_city()

    # Moving cars

    for car in cars:
        draw_car(car)

    # Detective

    draw_detective(95, 480, False)

    # Top information bar

    panel(
        pygame.Rect(18, 10, 864, 50),
        (10, 15, 35),
        GOLD
    )

    text(
        "DETECTIVE MODE",
        38, 27, GOLD, FONT
    )

    text(
        "ATTEMPTS LEFT: " + str(attempts),
        680, 27, WHITE, FONT
    )

    # Suspects

    text(
        "THE THREE SUSPECTS",
        270, 70, GOLD, FONT
    )

    for i in range(3):

        draw_suspect(
            i,
            (265+i*200, 93, 175, 165)
        )

    # Main code panel

    panel(
        pygame.Rect(260, 270, 610, 190),
        (8, 15, 35),
        CYAN,
        15
    )

    text(
        "CRACK THE SECRET CODE",
        285, 283, GOLD, MEDIUM
    )

    text(
        "Enter three different digits from 1 to 9",
        285, 315, WHITE, SMALL
    )

    # Number display

    panel(
        pygame.Rect(470, 340, 190, 55),
        (3, 9, 24),
        GOLD,
        10
    )

    shown = "  ".join(guess) if guess else "_  _  _"

    image = BIG.render(shown, True, CYAN)

    screen.blit(
        image,
        image.get_rect(center=(565, 367))
    )

    # Feedback

    text(
        feedback,
        285, 420, WHITE, SMALL
    )

    # SPECIAL HINT DISPLAY

    text(
        "SPECIAL HINT:",
        285, 440, GOLD, SMALL
    )

    # Display the latest unlocked hint

    text(
        current_hint,
        390, 440, CYAN, SMALL
    )

    # Number keypad

    for i, digit in enumerate("123456789"):

        x = 270 + (i % 5)*67
        y = 475 + (i // 5)*43

        if i >= 5:
            x = 270 + (i-5)*67

        button(
            pygame.Rect(x, y, 55, 34),
            digit,
            BLUE
        )

    # Clear button

    button(
        pygame.Rect(625, 475, 95, 34),
        "CLEAR",
        RED
    )

    # Submit button

    button(
        pygame.Rect(730, 475, 120, 34),
        "SUBMIT",
        GREEN
    )

    text(
        "TYPE DIGITS ON YOUR KEYBOARD OR USE THE KEYPAD",
        270, 564, CYAN, SMALL
    )


# ==========================================================
# CHECK THE GUESS
# ==========================================================

def submit_guess():

    global attempts, guess, feedback
    global scene, wrong_attempts

    if len(guess) != 3:

        feedback = "Enter exactly three digits!"

        play(WRONG)

        return

    if len(set(guess)) != 3 or "0" in guess:

        feedback = "Use three different digits from 1 to 9!"

        play(WRONG)

        return

    # Check correct digits and positions

    exact = sum(
        guess[i] == secret_code[i]
        for i in range(3)
    )

    total = sum(
        digit in secret_code
        for digit in guess
    )

    # Winning condition

    if guess == secret_code:

        feedback = "CODE CRACKED! CRIMINAL IDENTIFIED!"

        history.append(
            (guess, "CASE SOLVED")
        )

        scene = "win"

        play(WIN_SOUND)

        return

    # Incorrect guess

    attempts -= 1
    wrong_attempts += 1

    misplaced = total - exact

    feedback = (
        "Correct digits: " + str(total)
        + " | Correct positions: " + str(exact)
    )

    history.append(
        (
            guess,
            "Digits: " + str(total)
            + " | Positions: " + str(exact)
        )
    )

    # Give a special hint after every 3 wrong guesses

    if wrong_attempts % 3 == 0:

        give_hint()

    else:

        play(WRONG)

    guess = ""

    # Out of attempts

    if attempts <= 0:

        scene = "lose"


# ==========================================================
# VICTORY AND FAILURE SCREENS
# ==========================================================

def result_screen(won):

    draw_city()

    for car in cars:
        draw_car(car)

    glow(
        450, 250, 220,
        (40, 120, 220)
    )

    if won:

        centered(
            "CASE SOLVED!",
            65, GREEN, TITLE
        )

        centered(
            "You cracked the secret code!",
            125, WHITE, MEDIUM
        )

        centered(
            "THE CRIMINAL IS:",
            180, GOLD, FONT
        )

        draw_suspect(
            criminal_index,
            (355, 210, 190, 190),
            True
        )

        centered(
            suspects[criminal_index]["name"],
            430, RED, MEDIUM
        )

        centered(
            "Excellent detective work!",
            470, GOLD, FONT
        )

    else:

        centered(
            "CASE FAILED!",
            65, RED, TITLE
        )

        centered(
            "The criminal escaped!",
            125, WHITE, MEDIUM
        )

        centered(
            "THE SECRET CODE WAS: " + secret_code,
            190, GOLD, BIG
        )

        centered(
            "THE CRIMINAL WAS:",
            260, WHITE, FONT
        )

        draw_suspect(
            criminal_index,
            (355, 290, 190, 190),
            True
        )

    button(
        pygame.Rect(330, 535, 240, 45),
        "NEW CASE",
        BLUE
    )


# ==========================================================
# HOME SCREEN
# ==========================================================

def home_screen():

    draw_city()

    for car in cars:
        draw_car(car)

    panel(
        pygame.Rect(100, 45, 700, 510),
        (10, 15, 35),
        GOLD,
        25
    )

    glow(
        450, 280, 170,
        (40, 90, 180)
    )

    centered(
        "THE DEDUCTIVE",
        105, GOLD, TITLE
    )

    centered(
        "GAME",
        165, WHITE, BIG
    )

    centered(
        "EVERY CLUE HAS A SECRET",
        225, CYAN, FONT
    )

    centered(
        "A NUMBER-GUESSING DETECTIVE MYSTERY",
        265, WHITE, SMALL
    )

    draw_detective(450, 475, True)

    button(
        pygame.Rect(315, 495, 270, 50),
        "START NEW CASE",
        BLUE
    )

    text(
        "MYSTERY EDITION | VERSION 4.0",
        25, 20, GOLD, SMALL
    )


# ==========================================================
# RESET GAME
# ==========================================================

def reset_game():

    global scene

    new_case()

    scene = "game"


# ==========================================================
# MAIN GAME LOOP
# ==========================================================

running = True

while running:

    clock.tick(60)

    update_rain()
    update_cars()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        # ---------------- MOUSE CONTROLS ----------------

        if event.type == pygame.MOUSEBUTTONDOWN:

            mx, my = event.pos

            if scene == "home":

                if pygame.Rect(
                    315, 495, 270, 50
                ).collidepoint(mx, my):

                    scene = "game"

                    play(CLICK)

            elif scene == "game":

                # Number keypad

                for i, digit in enumerate("123456789"):

                    x = 270 + (i % 5)*67
                    y = 475 + (i // 5)*43

                    if i >= 5:
                        x = 270 + (i-5)*67

                    if pygame.Rect(
                        x, y, 55, 34
                    ).collidepoint(mx, my):

                        if len(guess) < 3:

                            guess += digit

                            play(CLICK)

                # Clear button

                if pygame.Rect(
                    625, 475, 95, 34
                ).collidepoint(mx, my):

                    guess = ""

                    feedback = "Enter your three-digit guess."

                    play(CLICK)

                # Submit button

                if pygame.Rect(
                    730, 475, 120, 34
                ).collidepoint(mx, my):

                    submit_guess()

            elif scene in ("win", "lose"):

                if pygame.Rect(
                    330, 535, 240, 45
                ).collidepoint(mx, my):

                    reset_game()

                    play(CLICK)

        # ---------------- KEYBOARD CONTROLS ----------------

        if event.type == pygame.KEYDOWN:

            if scene == "game":

                if event.key == pygame.K_BACKSPACE:

                    guess = guess[:-1]

                elif event.key == pygame.K_RETURN:

                    submit_guess()

                elif (
                    event.unicode.isdigit()
                    and event.unicode != "0"
                    and len(guess) < 3
                ):

                    guess += event.unicode

                    play(CLICK)

            elif scene == "home":

                if event.key == pygame.K_RETURN:

                    scene = "game"

                    play(CLICK)

            elif scene in ("win", "lose"):

                if event.key == pygame.K_RETURN:

                    reset_game()

                    play(CLICK)

    # ---------------- DRAW SCREENS ----------------

    if scene == "home":

        home_screen()

    elif scene == "game":

        game_screen()

    elif scene == "win":

        result_screen(True)

    elif scene == "lose":

        result_screen(False)

    pygame.display.flip()


pygame.quit()
sys.exit()


