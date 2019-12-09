import gamebox
import pygame
import random
import math

camera = gamebox.Camera(600, 800)
player = gamebox.from_color(300, 400, "red", 20, 20)
player2 = gamebox.from_color(200, 200, "blue", 20, 20)
ball = gamebox.from_circle(300, 400, "white", 10)
frames = 0
has_thrown = False

def move_toward(leader, follower, speed):
    if abs(follower.x - leader.x) <= 5 and abs(follower.y - leader.y) <= 5:
        # Base Case: get closer
        ...
        # move_toward(leader, follower, 0.5)
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
def move_toward_beta(leader, follower, speed):
    run = leader.x - follower.x
    rise = leader.y - follower.y
    length = math.sqrt((rise * rise) + (run * run));
    unitX = run / length
    unitY = rise / length
    follower.x += unitX * speed
    follower.y += unitY * speed
def tick(keys):
    global frames, has_thrown
    if pygame.K_DOWN in keys:
        player.y += 5
    if pygame.K_UP in keys:
        player.y -= 5
    if pygame.K_LEFT in keys:
        player.x -= 5
    if pygame.K_RIGHT in keys:
        player.x += 5

    camera.clear("black")
    camera.draw(player)
    camera.draw(player2)
    camera.draw(ball)
    if has_thrown:
        move_toward_beta(player2, ball, 3)
    else:
        ball.x = player.x
        ball.y = player.y

    if pygame.K_SPACE in keys:
        has_thrown = True


    frames+=1


    camera.display()




gamebox.timer_loop(30, tick)