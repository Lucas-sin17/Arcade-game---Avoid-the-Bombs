# AVOID THE BOMBS


import tkinter as tk  # not used directly, but harmless
from random import *
from turtle import *
from freegames import vector

# -------------------------
# Timer state and functions
# -------------------------
seconds = 0
timer_running = True  # set to False to stop the timer

def update_timer():
    """Increment and redraw the on-screen timer if running."""
    global seconds, timer_running
    if not timer_running:
        return

    seconds += 1
    timer_pen.clear()
    timer_pen.write(f"Time: {seconds}s", font=("Arial", 16, "normal"))
    ontimer(update_timer, 1000)  # schedule next tick in 1s

# -------------------------
# Player movement & speed boost
# -------------------------
# Direction-only unit vectors (do NOT encode speed here)
DIR_N = vector(0, 1)
DIR_S = vector(0, -1)
DIR_E = vector(1, 0)
DIR_W = vector(-1, 0)
options = [DIR_N, DIR_S, DIR_E, DIR_W]  # used for bombs and initial player dir

player_speed = 4          # normal speed
boost_speed = 8           # speed while boosting
boost_active = False      # is boost currently on?
boost_duration_ms = 2000  # how long the boost lasts (2 seconds)

player = vector(0, 0)
current_dir = choice(options)  # player starts moving in a random direction

bombs = []
speeds = []
sizes = []  # (unused now, but keep if you plan to vary bomb sizes later)

def set_dir(d):
    """Set player's direction to one of the unit vectors."""
    global current_dir
    current_dir = d

def speed_boost():
    """Temporarily increase the player's speed when SPACE is pressed."""
    global player_speed, boost_active
    if boost_active:
        return  # already boosted; ignore repeated presses
    boost_active = True
    player_speed = boost_speed
    ontimer(end_boost, 500)

def end_boost():
    """End the boost and restore normal speed."""
    global player_speed, boost_active
    boost_active = False
    player_speed = 4  # back to normal

# -------------------------
# Game helpers & drawing
# -------------------------
def inside(point):
    """Return True if point on screen."""
    return -200 < point.x < 200 and -200 < point.y < 200

def draw(alive):
    """Draw screen objects."""
    clear()

    # Player
    goto(player.x, player.y)
    color('blue' if alive else 'red')
    dot(10)

    # Bombs
    color('black')
    for bomb in bombs:
        goto(bomb.x, bomb.y)
        dot(20)

    update()

def game_over():
    """Stop timer, show game over and final time."""
    global timer_running
    timer_running = False

    if seconds >= 60:
        goto(0, 0)
        color('green')
        write("YOU WIN!", align="center", font=("Arial", 20, "bold"))
    else:
        goto(0, 0)
        color('red')
        write("YOU LOSE!", align="center", font=("Arial", 20, "bold"))

    goto(0, -24)
    color('black')
    write(f"Final Time: {seconds}s", align="center", font=("Arial", 14, "normal"))
    goto(0, -50)
    color('black')
    write("Click R to restart", align="center", font=("Arial", 14, "normal"))

def move():
    """Update player and bomb positions."""
    # ---- Move player by direction * current speed
    step = vector(current_dir.x * player_speed, current_dir.y * player_speed)
    player.move(step)

    # ---- Move bombs
    for bomb, speed in zip(bombs, speeds):
        bomb.move(speed)

    # ---- Possibly spawn a new bomb
    if randrange(5) == 0:
        base_dir = choice(options)  # one of DIR_N/DIR_S/DIR_E/DIR_W
        offset = randrange(-199, 200)

        # Pick starting edge based on direction (compare by object identity)
        if base_dir is DIR_N:
            bomb = vector(offset, -199)
        elif base_dir is DIR_S:
            bomb = vector(offset, 199)
        elif base_dir is DIR_E:
            bomb = vector(-199, offset)
        else:  # DIR_W
            bomb = vector(199, offset)

        # --- RANDOM SPEED MAGNITUDE (change this range as you like)
        speed_multiplier = randrange(3, 8)  # random int 2..6 pixels per tick

        # Create speed vector with that magnitude along the chosen direction
        speed_vec = vector(base_dir.x * speed_multiplier, base_dir.y * speed_multiplier)

        bombs.append(bomb)
        speeds.append(speed_vec)

    # ---- Remove bombs that leave the screen
    for index in reversed(range(len(bombs))):
        bomb = bombs[index]
        if not inside(bomb):
            del bombs[index]
            del speeds[index]

    # ---- Check player out of bounds
    if not inside(player):
        draw(False)
        game_over()
        return

    # ---- Check collisions
    for bomb in bombs:
        if abs(bomb - player) < 15:
            draw(False)
            game_over()
            return

    # ---- Continue game
    draw(True)
    ontimer(move, 50)

def restart_game():
    """Reset all game state to start over."""
    global player, bombs, speeds, seconds, timer_running
    global player_speed, boost_active, current_dir

    # Reset player & direction/speed
    player = vector(0, 0)
    current_dir = choice(options)
    player_speed = 4
    boost_active = False

    # Clear bombs + speeds
    bombs.clear()
    speeds.clear()

    # Reset timer
    seconds = 0
    timer_running = True
    timer_pen.clear()
    update_timer()  # restart timer ticking

    # Clear game over text and restart loop
    clear()
    move()

# -------------------------
# Setup the turtle screen
# -------------------------
setup(420, 420, 370, 0)
bgcolor('lightblue')
hideturtle()
up()
tracer(False)

# Timer pen (separate, hidden turtle for text)
timer_pen = Turtle(visible=False)
timer_pen.up()
timer_pen.goto(-195, 180)

# Controls
listen()
# Arrow keys
onkey(lambda: set_dir(DIR_N), 'Up')
onkey(lambda: set_dir(DIR_S), 'Down')
onkey(lambda: set_dir(DIR_E), 'Right')
onkey(lambda: set_dir(DIR_W), 'Left')
# WASD
onkey(lambda: set_dir(DIR_N), 'w')
onkey(lambda: set_dir(DIR_S), 's')
onkey(lambda: set_dir(DIR_E), 'd')
onkey(lambda: set_dir(DIR_W), 'a')
# Restart + Speed boost
onkey(restart_game, 'r')
onkey(restart_game, 'R')
onkey(speed_boost, 'space')  # <-- PRESS SPACE TO BOOST

# Start timer and game loop
update_timer()
move()
done()
