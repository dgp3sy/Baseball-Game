import gamebox
import pygame
import random
import math

camera = gamebox.Camera(512, 512)



first_base = gamebox.from_color(405, 296, "white", 8, 8)
second_base = gamebox.from_color(256, 150, "white", 8, 8)
third_base = gamebox.from_color(107, 297, "white", 8, 8)
home_base = gamebox.from_color(256, 440, "white", 8, 8)
bases=[home_base,first_base,second_base,third_base]

batter=gamebox.from_color(270, 440, "red", 10, 10)
pitcher=gamebox.from_color(256,295, "purple", 10,10)
first_base_player=gamebox.from_color(393, 275, "purple", 10, 10)
second_base_player=gamebox.from_color(331, 190, "purple", 10, 10)
shortstop = gamebox.from_color(173, 190, "purple", 10, 10)
third_base_player=gamebox.from_color(112, 280, "purple", 10, 10)
catcher=gamebox.from_color(256, 455, "purple", 10, 10)
left_field = gamebox.from_color(37, 25, "purple", 10, 10)
center_field=gamebox.from_color(252, 10, "purple", 10, 10)
right_field=gamebox.from_color(475, 25, "purple", 10, 10)

players = [
    batter, pitcher, catcher,
    first_base_player, second_base_player, shortstop, third_base_player,
    left_field, right_field, center_field
]
fielders = [
    first_base_player, second_base_player, shortstop, third_base_player,
    left_field, right_field, center_field
]
basemen = []

bat=gamebox.from_color(260, 440, "orange", 15,4)
ball=gamebox.from_image(259, 295, "baseball_transparent.png")
ball.scale_by(0.01)

background = gamebox.from_image(256, 256, "background.jpg")
background.scale_by(0.5)

x_speed = 0
y_speed = 0
frames = 0
hit_power = 10
await_return=0
ball_hit_type=-1
is_pitch = False
is_hit=False
catcher_has_ball = False
is_return_pitch = False
return_ball=False
pitcher_has_ball = True
determine_hit = False
ball_in_play = False
fielder_has_ball = False
is_new_at_bat = True
need_to_reset=False
players_next_base=1
# metrics for game
outs = 0
strikes = 0
balls = 0
runs = 0
inning = 1
metrics = {
    "outs" : 0, "strikes" : 0, "balls": 0, "runs": 0, "inning" : 0
}
# List containing information if a player has reached the base:
#       0 = Home Base
#       1 = First Base
#       2 = Second Base
#       3 = Third Base
on_base = [False, False, False, False]
hit_power_bar = gamebox.from_color(135, 460, "red", 100, 10)
hit_distance_bar = gamebox.from_color(135, 480, "yellow", 100, 10)
power_slider = gamebox.from_color(hit_power_bar.x - hit_power_bar.width/2, hit_power_bar.y, "black", 5, 10)
distance_slider = gamebox.from_color(hit_distance_bar.x - hit_distance_bar.width/2, hit_distance_bar.y, "black", 5, 10)
slider_speed = 3
has_pressed_space_1=False
has_pressed_space_2=False


def draw_metrics():
    outs_circle_list = []
    out_draw = gamebox.from_text(425, 400, "Outs: ", 24, "white")
    if metrics["outs"] == 1:
        outs_circle_list = [gamebox.from_circle(420, 420, "white", 5)]
    elif metrics["outs"] == 2:
        outs_circle_list = [gamebox.from_circle(420, 420, "white", 5), gamebox.from_circle(420, 430, "white", 5)]
    elif metrics["outs"] == 3:
        metrics["inning"] += 1
        metrics["outs"] = 0
    at_bat_draw = gamebox.from_text(425, 450, str(metrics["strikes"]) + " - " + str(metrics["balls"]), 24, "white")
    runs_draw = gamebox.from_text(75, 400, "Score: " + str(metrics["runs"]), 24, "white")
    inning_draw = gamebox.from_text(75, 420, "Inning: " + str(metrics["inning"]), 24, "white")
    for item in outs_circle_list:
        camera.draw(item)
    camera.draw(out_draw)
    camera.draw(at_bat_draw)
    camera.draw(runs_draw)
    camera.draw(inning_draw)
    hit_distance_label = gamebox.from_text(hit_distance_bar.x - 95, hit_distance_bar.y, "Direction:", 24, "white")
    hit_power_label = gamebox.from_text(hit_power_bar.x - 85, hit_power_bar.y, "Power:", 24, "white")
    camera.draw(hit_distance_label)
    camera.draw(hit_power_label)
    camera.draw(hit_power_bar)
    camera.draw(hit_distance_bar)
    camera.draw(distance_slider)
    camera.draw(power_slider)
def draw_list(obj_list):
    for base in obj_list:
        camera.draw(base)
def distance(a, b):
    return math.sqrt((a.x-b.x) ** 2 + (a.y - b.y)**2)
def return_batter_to_mound():
    batter.x = 270
    batter.y = 440
def move_toward(leader, follower, speed):
    if abs(follower.x - leader.x) <= 5 and abs(follower.y - leader.y) <= 5:
        # Close enough: do nothing
        pass
    elif follower.x < leader.x and follower.y < leader.y:
        follower.x += speed
        follower.y += speed
    elif follower.x > leader.x and follower.y < leader.y:
        follower.x -= speed
        follower.y += speed
    elif follower.x < leader.x and follower.y > leader.y:
        follower.x += speed
        follower.y -= speed
    elif follower.x > leader.x and follower.y > leader.y:
        follower.x -= speed
        follower.y -= speed
    elif follower.x > leader.x:
        follower.x -= speed
    elif follower.x < leader.x:
        follower.x += speed
    elif follower.y > leader.y:
        follower.y -= speed
    elif follower.y < leader.y:
        follower.y += speed
def batter_movement(keys):
    global ball_in_play
    if pygame.K_UP in keys:
        batter.y -= 2
    if pygame.K_LEFT in keys:
        batter.x -= 2
    if pygame.K_RIGHT in keys:
        batter.x += 2
    if pygame.K_DOWN in keys:
        batter.y += 2
def slider_movement(slider, bar):
    global slider_speed
    if slider.x < 85:
        slider_speed *= -1
    if slider.x >  185:
        slider_speed *= -1

    slider.speedx = slider_speed
    slider.move_speed()
def draw_everything():
    camera.draw(second_base_player)
    camera.draw(background)
    draw_list(bases)
    draw_list(players)
    draw_list(basemen)
    draw_metrics()
    camera.draw(ball)
def normalize_to_range(val, new_min, new_max):
    # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
    return (((val - 86) * (new_max -new_min)) / (186 - 86)) + new_min
def is_ball_off_screen():
    return ball.x > 512 or ball.x < 0 or ball.y > 512 or ball.y < 0
def reset_fielder_positions():
    first_base_player.x, first_base_player.y = 393, 275
    second_base_player.x, second_base_player.y = 331, 190
    third_base_player.x, third_base_player.y = 112, 280
    left_field.x, left_field.y = 37, 25
    center_field.x, center_field.y = 252, 10
    right_field.x, right_field.y = 475, 25
    shortstop.x, shortstop.y = 173, 190
def new_pitch():
    global is_hit, is_new_at_bat, has_pressed_space_1, has_pressed_space_2, fielder_has_ball
    is_hit = False
    is_new_at_bat = True
    has_pressed_space_1 = False
    has_pressed_space_2 = False
    fielder_has_ball = False
    ball.x = pitcher.x
    ball.y = pitcher.y
    reset_fielder_positions()
def closest_player_to_ball():
    min_dist = float('inf')
    min_indx=0
    for i in range(len(fielders)):
        d = distance(fielders[i], ball)
        if d < min_dist:
            min_dist = d
            min_indx = i
    return fielders[min_indx]
def closest_player_to_base(player_chasing_ball):
    global players_next_base
    min_dist = float('inf')
    min_indx=0
    for i in range(len(fielders)):
        d = distance(fielders[i], bases[players_next_base])
        if d < min_dist and fielders[i] != player_chasing_ball:
            min_dist = d
            min_indx = i
    return fielders[min_indx]
def defense():
    # TODO : Right now you are using a greedy algorithm, such that the closest person to the ball chases the
    #  ball and the next closest person to the base goes to the base. What you want to do is have the angle of
    #  the ball calculated at the point where the ball hits the bat, and have the players move accordingly as
    #  they would in a normal game
    global fielder_has_ball, get_ball
    # closest player needs to move to the ball
    if not fielder_has_ball:
        get_ball = closest_player_to_ball()
        move_toward(ball, get_ball, 1)
    # next closest player needs to move to the base
    get_base = closest_player_to_base(get_ball)
    move_toward(bases[players_next_base], get_base, 1)
    for player in fielders:
        if player.touches(ball):
            fielder_has_ball = True
            # Throw to that defender
    if fielder_has_ball:
        move_toward(get_base, ball, 5)
    for player in fielders:
        if player.touches(bases[players_next_base]) and player.touches(ball):
            new_pitch()
            if not on_base[players_next_base]:
                metrics["outs"] += 1

def animate_hit(keys, power, distance):
    global is_hit, is_new_at_bat, need_to_reset, players_next_base
    camera.clear("black")
    if not fielder_has_ball:
        ball.y -= normalize_to_range(power, 1, 5)
        ball.x += normalize_to_range(distance, -15, 15)
    draw_everything()
    defense()
    batter_movement(keys)
    if batter.touches(bases[players_next_base]):
        on_base[players_next_base] = True
        if players_next_base < 3:
            players_next_base+=1
        else:
            players_next_base=0
    if is_ball_off_screen():
        new_pitch()
    camera.display()
def animate_pitch(keys, pitch_speed):
    global has_pressed_space_2, has_pressed_space_1, is_new_at_bat, is_hit, hit_frames
    camera.clear("black")
    draw_everything()

    if not is_hit:
        if pygame.K_SPACE in keys:
            camera.draw(bat)
            if ball.touches(bat):
                is_hit = True
        ball.y += pitch_speed
    else:
        # hit_frames=0
        animate_hit(keys, power_slider.x, distance_slider.x)
    camera.display()
def tick(keys):
    global frames, is_pitch, catcher_has_ball, is_return_pitch, pitcher_has_ball, hit_power, is_new_at_bat, pitch_speed
    global has_pressed_space_1, has_pressed_space_2
    if is_new_at_bat:
        pitch_speed = random.randint(3, 10)
        camera.clear("black")
        if has_pressed_space_1 and has_pressed_space_2:
            is_new_at_bat = False
        if pygame.K_s in keys and has_pressed_space_1 and not has_pressed_space_2:
            has_pressed_space_2 = True
        if pygame.K_a in keys and not has_pressed_space_1 and not has_pressed_space_2:
            has_pressed_space_1 = True
        if not has_pressed_space_1 and not has_pressed_space_2:
            slider_movement(power_slider, hit_power_bar)
        if not has_pressed_space_2 and has_pressed_space_1:
            slider_movement(distance_slider, hit_distance_bar)


        frames += 1
        draw_everything()
        camera.display()

    else:
        animate_pitch(keys, pitch_speed)




    # defense(fielders)


    # Cursor location used for game creation
    # if frames % 10 == 0:
    #     print(pygame.mouse.get_pos())



gamebox.timer_loop(45, tick)