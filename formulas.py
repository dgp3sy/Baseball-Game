import math

def xy_to_degree(delta_x, delta_y):
    rads = math.atan2(delta_y, delta_x)
    return math.degrees(rads)

