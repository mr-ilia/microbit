# MakeCode Python. Hold the board still at startup, then tilt it.
MOTION_THRESHOLD = 150  # milli-g
basic.pause(1000)
start_x = input.acceleration(Dimension.X)
start_y = input.acceleration(Dimension.Y)
start_z = input.acceleration(Dimension.Z)

while True:
    dx = abs(input.acceleration(Dimension.X) - start_x)
    dy = abs(input.acceleration(Dimension.Y) - start_y)
    dz = abs(input.acceleration(Dimension.Z) - start_z)
    if max(dx, max(dy, dz)) > MOTION_THRESHOLD:
        basic.show_icon(IconNames.NO)
    else:
        basic.clear_screen()
    basic.pause(50)
