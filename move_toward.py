import gamebox
import pygame
import random

camera = gamebox.Camera(600, 800)
player = gamebox.from_color(300, 400, "red", 20, 20)
follower = gamebox.from_color(200, 200, "blue", 20, 20)
frames = 0

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

def tick(keys):
    global frames
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
    camera.draw(follower)
    move_toward(player, follower, 2)


    frames+=1


    camera.display()




gamebox.timer_loop(30, tick)