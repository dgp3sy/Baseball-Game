import gamebox
import pygame
import random
import formulas
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
angle=45
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
is_double_play=False
is_foul_ball = False
has_swung=False
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

on_base = [False, False, False, False]
hit_power_bar = gamebox.from_color(135, 460, "red", 100, 10)
hit_distance_bar = gamebox.from_color(135, 480, "yellow", 100, 10)
hit_direction_good = gamebox.from_color(135, 480, "dark green", 30, 10)
power_slider = gamebox.from_color(hit_power_bar.x - hit_power_bar.width/2, hit_power_bar.y, "black", 5, 10)
distance_slider = gamebox.from_color(hit_distance_bar.x - hit_distance_bar.width/2, hit_distance_bar.y, "black", 5, 10)
slider_speed = 3
has_pressed_space_1=False
has_pressed_space_2=False

def handle_metrics():
    '''
    Determines metrics of the games including: strokes, outs, innings, balls. If they reach a certain threshorld, the
    function alters the according feature. For example, if you reach three strikes, strikes goes back to 0, outs is increased
    by one, per the rules of the game. All metrics of the game are kept in a HashTable for quick access
    :return:
    '''
    # Three strikes, you're out
    if metrics["strikes"] >= 3:
        metrics["outs"] += 1
        metrics["strikes"] =0
        metrics["balls"] = 0
    # Three outs ends the inning
    if metrics["outs"] >= 3:
        metrics["inning"] += 1
        metrics["outs"] = 0
        metrics["strikes"] = 0
        metrics["balls"] = 0
    # Four balls is a walk
    if metrics["balls"] >= 4:
        metrics["strikes"] = 0
        metrics["balls"] = 0
def draw_metrics():
    '''
    Displays metrics to the screen, see handle_metrics() function for dealing with changes in the game
    :return:
    '''
    handle_metrics()
    outs_circle_list = []
    out_draw = gamebox.from_text(425, 400, "Outs: ", 24, "white")
    if metrics["outs"] == 1:
        outs_circle_list = [gamebox.from_circle(420, 420, "white", 5)]
    elif metrics["outs"] == 2:
        outs_circle_list = [gamebox.from_circle(420, 420, "white", 5), gamebox.from_circle(430, 420, "white", 5)]

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
    camera.draw(hit_direction_good)
    camera.draw(distance_slider)
    camera.draw(power_slider)
def draw_list(obj_list):
    '''
    Given a list of objects, draw all the objects in the list
    :param obj_list: A list of gamebox objects, could be either from_image or from_color objects
    :return:
    '''
    for base in obj_list:
        camera.draw(base)
def distance(a, b):
    '''
    given two points on a cartesian plane, returns the distance between them. Objects passed through the function must
    have fields for accessing x and y value. For example, gamebox objects have a field where you can access that object's
    x location by calling .x
    :param a: Gamebox Object 1
    :param b: Gamebox Object 2
    :return: Distance between Gamebox Object 1 and Gamebox Object 2 on a cartesian plane (in terms of pixels)
    '''
    return math.sqrt((a.x-b.x) ** 2 + (a.y - b.y)**2)
def return_batter_to_mound():
    '''
    returns the batter to its starting location - called at the end of plays to reset interface
    :return:
    '''
    batter.x = 270
    batter.y = 440
def move_toward(leader, follower, speed):
    '''
    Moves one object toward another by calculating the angle in which they are against one another, and determines the
    shortest path to that person. This could be considered "greedy" in the context of the baseball game. For example,
    if the ball is coming toward the outfielder, he will move directly toward the ball (moving forward as well as side to
    side). This may cause the ball to go past him. In this scenario, if the player moved laterally (to cut of the trajectory
    path of the ball) he may be able to catch the ball. This is what baseball players actually do. However, for the context
    of this problem, this was the easiest method to implement to have two objects move toward one another
    :param leader: What the person is moving toward (usually something like a base or the baseball)
    :param follower: The person that needs to be moved
    :param speed: The speed in which they should move (currently I am using 1 for running and 3 for throwing, this may change
    depending on design decisions). The speed is in terms of pixels moved per frames, with 45 frames per second
    :return: None
    '''
    run = leader.x - follower.x
    rise = leader.y - follower.y
    length = math.sqrt((rise * rise) + (run * run))
    unitX = run / length
    unitY = rise / length
    follower.x += unitX * speed
    follower.y += unitY * speed
def batter_movement(keys):
    '''
    Allows the batter to run the bases, this function is called after the ball is hit
    :param keys:
    :return:
    '''
    global ball_in_play
    if pygame.K_UP in keys:
        batter.y -= 2
    if pygame.K_LEFT in keys:
        batter.x -= 2
    if pygame.K_RIGHT in keys:
        batter.x += 2
    if pygame.K_DOWN in keys:
        batter.y += 2
def slider_movement(slider, speed_multiplier=1):
    '''
    Slider movement back and forth along the power or distance bar
    :param slider: (gamebox object) Which slider to move
    :param speed: (float or int) What speed to move it at (default value is 1 pixel per frame) - Higher numbers make the slider go faster,
    while decimals make the slider move slower. For example, a speed_multiple of 2 would make the slider speed move twice as
    fast
    :return:
    '''
    global slider_speed
    if slider.x < 85:
        slider_speed *= -1
    if slider.x >  185:
        slider_speed *= -1

    slider.speedx = slider_speed * speed_multiplier
    slider.move_speed()
def draw_everything():
    '''
    Draw everything defined in the game
    :return:
    '''
    camera.draw(second_base_player)
    camera.draw(background)
    draw_list(bases)
    draw_list(players)
    draw_list(basemen)
    draw_metrics()
    camera.draw(ball)
def normalize_to_range(val, new_min, new_max, old_min=86, old_max=186):
    '''
    Given a value with a range of 86, and 186, normalize that value to a specific range. This function is used because
    it takes the range of the location of the x value of the slider (which can be in between 86 and 186, and normalizes
    it to range of the speed of the ball
    :param val: (int) incoming number - expected value to be between 86 and 186
    :param new_min: (int) New minimum value of intended range
    :param new_max: (int) New maximum value of intended range
    :param old_min: (int) Old min of previous range
    :param old_max: (int) Old min of previous range
    :return:
    '''
    # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
    return (((val - old_min) * (new_max -new_min)) / (old_max - old_min)) + new_min
def is_strike():
    '''
    Determines if the ball moves below the screen
    :return: Boolen value: true if it is below the screen
    '''
    return ball.y > 512
def is_ball_off_screen():
    '''
    Determines if the ball goes off the screen on the left, right, or top edge, signifying a hit
    :return: Boolean value if the ball is off the screen
    '''
    return ball.x > 512 or ball.x < 0 or ball.y > 512 or ball.y < 0
def reset_fielder_positions():
    '''
    Resets all the positions of the players after the play is over. These locations are the same as what they are
    initialized to at the start of the game
    :return:
    '''
    first_base_player.x, first_base_player.y = 393, 275
    second_base_player.x, second_base_player.y = 331, 190
    third_base_player.x, third_base_player.y = 112, 280
    left_field.x, left_field.y = 37, 25
    center_field.x, center_field.y = 252, 10
    right_field.x, right_field.y = 475, 25
    shortstop.x, shortstop.y = 173, 190
    pitcher.x, pitcher.y = 256,295
def new_pitch():
    '''
    Resets player locations, boolean flags, and other values to reset the screen for the next pitch. Pretty useful function
    if I do say so myself. Call this when you want a new pitch to happen.
    :return:
    '''
    global is_hit, is_new_at_bat, has_pressed_space_1, has_pressed_space_2, fielder_has_ball, is_double_play, is_foul_ball, has_swung
    if is_foul_ball:
        if metrics["strikes"] < 2:
            metrics["strikes"] += 1
    is_foul_ball=False
    is_hit = False
    is_new_at_bat = True
    has_pressed_space_1 = False
    has_pressed_space_2 = False
    fielder_has_ball = False
    is_double_play = False
    has_swung = False
    reset_fielder_positions()
    ball.x = pitcher.x
    ball.y = pitcher.y
def closest_player_to_ball():
    '''
    Determines the closest fielder to the ball. Iterates through all the players in the list, determines the distance
    between that player and the ball and keeps track of that player if they are less than the current min. This method
    follows the old style of gameplay with a very greedy approach such that the closest player to the ball chases the
    ball.
    :return: (Gamebox Object) of the fielder that is closest to the ball, this value is then used such that they start
    moving toward the ball
    '''
    min_dist = float('inf')
    min_indx=0
    for i in range(len(fielders)):
        d = distance(fielders[i], ball)
        if d < min_dist:
            min_dist = d
            min_indx = i
    return fielders[min_indx]
def closest_player_to_base(player_chasing_ball):
    '''
    Determines the closest fielder to the next base. Iterates through all the players in the list, determines the distance
    between that player and the ball and keeps track of that player if they are less than the current min. This method
    follows the old style of gameplay with a very greedy approach such that the closest player to the next base goes to that
    base. Determines first if the player is currently chasing the ball, which is the priority
    :return: (Gamebox Object) of the fielder that is closest to the next base, this value is then used such that they start
    moving toward the base to get ready to tag the plate before the runner arrives
    '''
    global players_next_base
    min_dist = float('inf')
    min_indx=0
    for i in range(len(fielders)):
        d = distance(fielders[i], bases[players_next_base])
        if d < min_dist and fielders[i] != player_chasing_ball:
            min_dist = d
            min_indx = i
    return fielders[min_indx]
def defense_based_on_ball_location():
    '''
    Right now you are using a greedy algorithm, such that the closest person to the ball chases the
    ball and the next closest person to the base goes to the base. What you want to do is have the angle of
    the ball calculated at the point where the ball hits the bat, and have the players move accordingly as
    they would in a normal game
    '''
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
def new_play(player_getting_ball, player_getting_base, base=first_base, is_double=False):
    '''
    Defines movement of players while the ball is in play
    :param player_getting_ball: This player rushes toward the ball
    :param player_getting_base: This player goes to the next base
    :param base: The base that they are trying to throw to - should be the lead runner, but is default to first base
    for the easy out
    :param is_double: Boolean flag to determine if there is a possibility for a double play
    :return:
    '''
    global get_ball, get_base, fielder_has_ball, is_double_play
    get_ball = player_getting_ball
    get_base = player_getting_base
    move_toward(ball, get_ball, 1)
    move_toward(base, get_base, 1)
    if get_ball.touches(ball):
        fielder_has_ball = True
        if is_double:
            is_double_play = True
def outfielder_backup(outfielder, base=first_base):
    '''
    When the ball is in play, this outfielder should backup the ball in case the infielder misses it
    :param outfielder: Which outfielder should backup the ball
    :param base: The base they need to throw to - not needed, since once the player touches the ball, they will set off
    the boolean flag that will throw the ball to the next base
    :return:
    '''
    global fielder_has_ball
    move_toward(ball, outfielder, 1)
    if outfielder.touches(ball):
        fielder_has_ball=True
def hit_ball(power, direction):
    '''
    Given power and direction of the ball, determines the angle off the bat and moves the ball image according to x
    and y values normalized for the game.
    :param power: Y distance
    :param direction: X Distance
    :return: angle the ball hits off the bat, where first base is about 130 degrees and third base is about 43 degrees, and
    second plate is 90 degrees
    '''
    ball.y -= normalize_to_range(power, 1, 5)
    ball.x += normalize_to_range(direction, -10, 10)
    return formulas.xy_to_degree(normalize_to_range(power, 1, 5), normalize_to_range(direction, -15, 15)) + 90
def defense_based_on_angle(a):
    # TODO : Keep track of leading base and try to get that runner out
    global fielder_has_ball, get_ball, get_base, is_double_play, is_foul_ball
    if not fielder_has_ball:
        if a < 30 : # left tip foul, do nothing
            is_foul_ball = True
        # third base chase - throw to first
        if 30 <= a < 70:
            outfielder_backup(left_field)
            new_play(third_base_player, first_base_player)
        # double play at second and first
        elif 50 <= a < 70:
            # Shortstop is fetching ball
            outfielder_backup(center_field)
            new_play(shortstop, second_base_player, second_base, True)
        # Pitcher throws to first
        elif 70 <= a < 93:
            new_play(pitcher, first_base_player)
        # second base throws to first base player
        elif 93 <= a < 105:
            outfielder_backup(right_field)
            new_play(second_base_player, first_base_player)
        elif 105 <= a < 130:
            new_play(right_field, first_base_player)
        elif 130 <= a < 150:
            new_play(right_field, first_base_player)
        if a >= 150:  #  right tip foul - don't do anything
            is_foul_ball = True

    if fielder_has_ball:
        if is_double_play:
            move_toward(get_base, ball, 3) # ball coming toward second base
            if second_base_player.touches(ball):
                # initiate throw to first
                is_double_play = False
                get_base = first_base_player
        else:
            # ball heading to first base now
            move_toward(get_base, ball, 3)
            move_toward(first_base, first_base_player, 1)
            if first_base_player.touches(first_base) and first_base_player.touches(ball):
                new_pitch()
                if not on_base[players_next_base]:
                    if not is_double_play:
                        metrics["outs"] += 1
                    if is_double_play:
                        metrics["outs"] += 2
def animate_hit(keys, power, direction):
    '''
    Shows the ball once the player hits the ball with the bat. This tick function determines the gameplay of the defense
    and will eventually show base running
    :param keys: Key input from user
    :param power: Power that they had on the scrollbar
    :param direction: direction they had on the scrollbar
    :return:
    '''
    # TODO : Scoring runs
    # TODO : Base Running
    # TODO : Keeping track of strikes
    # TODO : keep track of outs
    global is_hit, is_new_at_bat, need_to_reset, players_next_base, angle
    camera.clear("black")
    if not fielder_has_ball:
        angle = hit_ball(power, direction)

    draw_everything()
    # defense_based_on_ball_location()
    defense_based_on_angle(angle)
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
    '''
    Shows the pitch once the player makes decisions of the power and distance meter. This tick function determines
    if the ball is hit or is a strike
    :param keys: Key input from user
    :param pitch_speed: Speed that the pitcher throws the ball - currently random number but could be generated some other way
    :return:
    '''
    # TODO : Catcher
    # TODO : pitch_type parameter that allows the pitcher to throw curveballs, fastballs, splitters, etc. Could write
    #  an enumerated class to achieve this
    global has_pressed_space_2, has_pressed_space_1, is_new_at_bat, is_hit, hit_frames, has_swung
    camera.clear("black")
    draw_everything()
    if not is_hit and not catcher_has_ball:
        if pygame.K_SPACE in keys:
            camera.draw(bat)
            has_swung = True
            if ball.touches(bat):
                is_hit = True
        ball.y += pitch_speed
        if is_strike():
            if has_swung:
                metrics["strikes"] += 1
                new_pitch()
            else:
                metrics["balls"] += 1
                new_pitch()
    else:
        # hit_frames=0
        animate_hit(keys, power_slider.x, distance_slider.x)
    camera.display()
def tick(keys):
    '''
    Main tick function first called by the timer loop. This function allows the user to hit the scroll bar to determine
    the power and direction the ball will come off the bat
    :param keys: user input
    :return:
    '''
    global frames, is_pitch, catcher_has_ball, is_return_pitch, pitcher_has_ball, hit_power, is_new_at_bat, pitch_speed
    global has_pressed_space_1, has_pressed_space_2
    if is_new_at_bat:
        pitch_speed = random.randint(3, 20)
        camera.clear("black")
        if has_pressed_space_1 and has_pressed_space_2:
            is_new_at_bat = False
        if pygame.K_s in keys and has_pressed_space_1 and not has_pressed_space_2:
            has_pressed_space_2 = True
        if pygame.K_a in keys and not has_pressed_space_1 and not has_pressed_space_2:
            has_pressed_space_1 = True
        if not has_pressed_space_1 and not has_pressed_space_2:
            slider_movement(power_slider)
        if not has_pressed_space_2 and has_pressed_space_1:
            slider_movement(distance_slider)


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