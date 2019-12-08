import gamebox
import pygame
import random

camera = gamebox.Camera(512, 512)



first_base = gamebox.from_color(405, 296, "white", 8, 8)
second_base = gamebox.from_color(256, 150, "white", 8, 8)
third_base = gamebox.from_color(107, 297, "white", 8, 8)
home_base = gamebox.from_color(256, 440, "white", 8, 8)
bases=[first_base,second_base,third_base,home_base]

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
    pitcher, catcher,
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
defense_has_ball = False

# metrics for game
outs = 0
strikes = 0
balls = 0
runs = 0
inning = 1
metrics = {
    "outs" : 0, "strikes" : 0, "balls": 0, "runs": 0, "inning" : 0
}


def draw_metrics():
    outs_circle_list = []
    out_draw = gamebox.from_text(425, 400, "Outs: ", 24, "white")
    if metrics["outs"] == 1:
        outs_circle_list = [gamebox.from_circle(420, 420, "white", 5)]
    elif metrics["outs"] == 2:
        outs_circle_list = [gamebox.from_circle(420, 420, "white", 5), gamebox.from_circle(420, 430, "white", 5)]
    elif metrics["outs"] == 3:
        metrics[4] += 1
        metrics["outs"] = 0

    at_bat_draw = gamebox.from_text(425, 450, str(metrics["strikes"]) + " - " + str(metrics["balls"]), 24, "white")
    runs_draw = gamebox.from_text(75, 400, "Score: " + str(metrics["runs"]), 24, "white")
    inning_draw = gamebox.from_text(75, 450, "Inning: " + str(metrics["inning"]), 24, "white")
    for item in outs_circle_list:
        camera.draw(item)
    camera.draw(out_draw)
    camera.draw(at_bat_draw)
    camera.draw(runs_draw)
    camera.draw(inning_draw)
def draw_list(obj_list):
    for base in obj_list:
        camera.draw(base)

def new_hit():
    xspeed = random.randint(-5,5)
    yspeed = random.randint(1,10)
    return xspeed, yspeed

def pitch_ball():
    global is_pitch, catcher_has_ball, is_return_pitch, await_return, return_ball, pitcher_has_ball, determine_hit
    if is_pitch and ball.y < catcher.y:
        ball.y += 7
    if ball.y >= catcher.y:
        is_pitch = False
        catcher_has_ball = True
    if catcher_has_ball:
        await_return += 1
        if await_return % 25 == 0:
            return_ball = True
        if return_ball and ball.y > pitcher.y:
            ball.y -= 3
        if ball.y <= pitcher.y:
            # reset flags for next pitch
            await_return=0
            catcher_has_ball=False
            return_ball=False
            pitcher_has_ball=True
def batting(keys):
    global is_pitch, is_hit, ball_hit_type, pitcher_has_ball, determine_hit, ball_in_play, defense_has_ball
    global x_speed, y_speed

    is_batting=False
    if pygame.K_SPACE in keys:
        camera.draw(bat)
        is_batting=True
    if is_batting and ball.touches(bat):
        is_pitch=False
        is_hit=True
    if is_hit:
        ball_hit_type = random.randint(0,5)
        is_hit=False
        pitcher_has_ball=False
        determine_hit = True
    if not pitcher_has_ball and determine_hit:
        x_speed, y_speed = new_hit()
        determine_hit = False
    if not pitcher_has_ball and not defense_has_ball:
        ball_in_play = True
        ball.x += x_speed
        ball.y -= y_speed
    if not pitcher_has_ball:
        run_bases(keys)
    if pitcher_has_ball and (batter.x, batter.y) != (270, 440):
        return_batter_to_mound()


def return_batter_to_mound():
    batter.x = 270
    batter.y = 440


def ball_off_screen_check():
    global pitcher_has_ball, ball_in_play
    # HIT!!
    if (ball.x < 0 and ball.y < 200) or (ball.x > 512 and ball.y < 204) or (ball.y < -20):
        # new batter comes to mound when batter gets to first
        if batter.touches(first_base):
            if len(basemen) == 0:
                basemen.append(gamebox.from_color(390, 275, "red", 10, 10))
            ball.x = 259
            ball.y = 295
            pitcher_has_ball=True
            ball_in_play = False
            metrics["runs"] += 1
    # Foul ball
    elif(ball.x < 0) or ball.x > 512 or ball.y > 522:
        ball.x = 259
        ball.y = 295
        pitcher_has_ball=True
        ball_in_play = False
        if (metrics["strikes"] != 2):
            metrics["strikes"] += 1

def defense(player_list):
    global ball_in_play, pitcher_has_ball, defense_has_ball, is_pitch
    if ball_in_play:
        for player in player_list:
            if player.touches(ball):
                ball.x += 0
                ball.y += 0
                ball_in_play = False
                defense_has_ball=True
                metrics["outs"] += 1
    if defense_has_ball:
        # if ball.y < pitcher.y:
        #     ball.y += 3
        # if ball.y > pitcher.y:
        #     ball.y -= 3
        # if ball.x < pitcher.x:
        #     ball.x += 3
        # if ball.x > pitcher.x:
        #     ball.x -= 3
        # move_toward(ball, pitcher, 2)
        if ball.y - pitcher.y <= 3 and ball.x - pitcher.x <= 3:
            pitcher_has_ball=True

def move_toward(moveable_obj, stationary_obj, speed):
    dx, dy = (stationary_obj.x - moveable_obj.y, stationary_obj.y - moveable_obj.y)
    stepx, stepy = (dx / speed, dy / speed)
    ball.move(moveable_obj.x + stepx, moveable_obj.y + stepy)

def run_bases(keys):
    global ball_in_play
    if pygame.K_UP in keys:
        batter.y -= 2
    if pygame.K_LEFT in keys:
        batter.x -= 2
    if pygame.K_RIGHT in keys:
        batter.x += 2
    if pygame.K_DOWN in keys:
        batter.y += 2



def tick(keys):
    global frames, is_pitch, catcher_has_ball, is_return_pitch, pitcher_has_ball

    camera.clear("black")
    if pitcher_has_ball and pygame.K_a in keys:
        is_pitch = True


    defense(fielders)
    ball_off_screen_check()
    pitch_ball()
    frames+=1
    camera.draw(background)
    draw_list(bases)
    draw_list(players)
    draw_list(basemen)
    draw_metrics()
    batting(keys)

    camera.draw(ball)
    camera.display()

    # Cursor location used for game creation
    # if frames % 10 == 0:
    #     print(pygame.mouse.get_pos())



gamebox.timer_loop(30, tick)