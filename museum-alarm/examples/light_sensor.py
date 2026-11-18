# MakeCode Python. Cover the LED display, then let light reach it.
LIGHT_THRESHOLD = 50

while True:
    light = input.light_level()
    if light > LIGHT_THRESHOLD:
        basic.show_icon(IconNames.NO)
    else:
        basic.clear_screen()
    basic.pause(50)
