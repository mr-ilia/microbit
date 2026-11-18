# MakeCode Python. Cover the LED display, then let light reach it.
LIGHT_THRESHOLD = 50

while True:
    if input.light_level() > LIGHT_THRESHOLD:
        basic.show_icon(IconNames.NO)
    else:
        basic.clear_screen()
    basic.pause(50)
