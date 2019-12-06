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

bat=gamebox.from_color(260, 440, "orange", 15,4)
ball=gamebox.from_image(259, 295, "baseball_transparent.png")
ball.scale_by(0.01)

background = gamebox.from_image(256, 256, "background.jpg")
background.scale_by(0.5)

frames = 0
await_return=0
ball_hit_type=-1
is_pitch = False
is_hit=False
catcher_has_ball = False
is_return_pitch = False
return_ball=False
pitcher_has_ball = True


def draw_list(obj_list):
    for base in obj_list:
        camera.draw(base)
def pitch_ball():
    global is_pitch, catcher_has_ball, is_return_pitch, await_return, return_ball, pitcher_has_ball
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
    global is_pitch, is_hit, ball_hit_type, pitcher_has_ball
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
    if not pitcher_has_ball:
        hit_motion(ball_hit_type)

def hit_motion(num):
    # Third Base
    if num == 0:
        ball.x -= 5
        ball.y -= 5
    # First Base - Foul
    if num == 1:
        ball.x += 5
        ball.y -= 4
    # Fould Ball
    if num == 2:
        ball.x -= 7
        ball.y -= 3
    # Line Drive to Left Field
    if num == 3:
        ball.x -= 3
        ball.y -= 8
    # Line Drive to Right Field
    if num == 4:
        ball.x += 3
        ball.y -= 7


def ball_off_screen_check():
    global pitcher_has_ball
    if ball.x < -10 or ball.x > 522 or ball.y < -10 or ball.y > 522:
        ball.x = 259
        ball.y = 295
        pitcher_has_ball=True




def tick(keys):
    global frames, is_pitch, catcher_has_ball, is_return_pitch, pitcher_has_ball

    camera.clear("black")
    if pitcher_has_ball and pygame.K_a in keys:
        is_pitch = True



    ball_off_screen_check()
    pitch_ball()
    frames+=1
    camera.draw(background)
    draw_list(bases)
    draw_list(players)
    batting(keys)
    camera.draw(ball)
    camera.display()




gamebox.timer_loop(30, tick)