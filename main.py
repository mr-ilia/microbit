# MISSION IMPOSSIBLE: MUSEUM BOX - MakeCode Python
# A: change mode while disarmed. B: arm, cancel or reset.
# Close the box during the 5-second countdown, then keep it still.

# ---------- CHANGE THESE SETTINGS ----------
MODE = "BOTH"             # "LIGHT", "MOTION", or "BOTH" (light OR motion)
LIGHT_THRESHOLD = 50      # 0-255. Trigger above this light level.
MOTION_THRESHOLD = 150    # milli-g. Trigger above this axis change.
CONFIRM_MS = 100          # Trigger must remain true for this long.
SOUND_ENABLED = True      # V2 speaker; V1 can use a P0/GND speaker.
RADIO_ENABLED = False     # Optional: needs a MakeCode radio receiver.
RADIO_GROUP = 8
# ------------------------------------------
ARM_DELAY_MS = 5000
CALIBRATION_MS = 1000
LOOP_MS = 20

mode = MODE
state = "DISARMED"
note = ""
baseline = [0, 0, 0]
total = [0, 0, 0]
low = [0, 0, 0]
high = [0, 0, 0]
samples = 0
brightest = 0
since = 0
candidate = -1
shown = ""
was_a = False
was_b = False
alarm_since = 0
next_radio = 0
tone_on = False


def alarm_rule(selected_mode: str, light_alarm: bool, motion_alarm: bool):
    # The Boolean logic for this lesson:
    if selected_mode == "LIGHT":
        return light_alarm
    if selected_mode == "MOTION":
        return motion_alarm
    return light_alarm or motion_alarm


def motion_change(axes: List[number]):
    # Compare each axis with the fixed position saved during calibration.
    # This detects tilting as well as shaking.
    return max(abs(axes[0] - baseline[0]),
               max(abs(axes[1] - baseline[1]), abs(axes[2] - baseline[2])))


def update_alarm(now: number, a: bool, b: bool, light: number, axes: List[number]):
    global state, note, candidate, since, mode
    global total, low, high, samples, brightest, baseline
    # B has priority: resetting the alarm cannot trigger it again.
    if b:
        note = ""
        candidate = -1
        if state == "DISARMED":
            state = "COUNTDOWN"
            since = now
        else:
            state = "DISARMED"
        return

    if state == "DISARMED":
        if a:
            if mode == "LIGHT":
                mode = "MOTION"
            elif mode == "MOTION":
                mode = "BOTH"
            else:
                mode = "LIGHT"
            note = ""
        return

    if state == "COUNTDOWN":
        if now - since >= ARM_DELAY_MS:
            state = "CALIBRATING"
            since = now
            total = [0, 0, 0]
            low = [32767, 32767, 32767]
            high = [-32767, -32767, -32767]
            samples = 0
            brightest = 0
        return

    if state == "CALIBRATING":
        samples += 1
        brightest = max(brightest, light)
        for i in range(3):
            total[i] += axes[i]
            low[i] = min(low[i], axes[i])
            high[i] = max(high[i], axes[i])
        if now - since >= CALIBRATION_MS:
            spread = max(high[0] - low[0], max(high[1] - low[1], high[2] - low[2]))
            if mode != "LIGHT" and spread > MOTION_THRESHOLD:
                state = "DISARMED"
                note = "STILL"
            elif mode != "MOTION" and brightest > LIGHT_THRESHOLD:
                state = "DISARMED"
                note = "DARK"
            else:
                for j in range(3):
                    baseline[j] = Math.floor(total[j] / samples)
                state = "ARMED"
                candidate = -1
        return

    if state == "ARMED":
        light_alarm = light > LIGHT_THRESHOLD
        motion_alarm = motion_change(axes) > MOTION_THRESHOLD
        trigger = alarm_rule(mode, light_alarm, motion_alarm)
        if not trigger:
            candidate = -1
        elif candidate < 0:
            candidate = now
        elif now - candidate >= CONFIRM_MS:
            state = "ALARM"
    # The alarm stays latched even when the box becomes dark/still again.


def run_tick():
    global was_a, was_b, alarm_since, next_radio, shown, tone_on
    now = input.running_time()
    a_down = input.button_is_pressed(Button.A)
    b_down = input.button_is_pressed(Button.B)
    old_state = state
    update_alarm(now, a_down and not was_a, b_down and not was_b,
                 input.light_level(), [input.acceleration(Dimension.X),
                                       input.acceleration(Dimension.Y),
                                       input.acceleration(Dimension.Z)])
    was_a = a_down
    was_b = b_down
    if state == "ALARM" and old_state != "ALARM":
        alarm_since = now
        next_radio = now

    # One short display update keeps B responsive in every state.
    symbol = ""
    if state == "DISARMED":
        if note != "":
            symbol = note.char_at(Math.idiv(now, 250) % (len(note) + 2))
        elif mode == "LIGHT":
            symbol = "L"
        elif mode == "MOTION":
            symbol = "M"
        else:
            symbol = "O"
    elif state == "COUNTDOWN":
        symbol = str(max(1, Math.ceil((ARM_DELAY_MS - (now - since)) / 1000)))
    elif state == "ARMED":
        symbol = "."
    elif state == "ALARM" and Math.idiv(now - alarm_since, 250) % 2 == 0:
        symbol = "X"
    if symbol != shown:
        basic.clear_screen()
        if symbol == ".":
            led.plot_brightness(2, 2, 25)
        elif symbol != "":
            basic.show_string(symbol, 1)
        shown = symbol

    should_sound = state == "ALARM" and SOUND_ENABLED and (now - alarm_since) % 500 < 180
    if should_sound != tone_on:
        if should_sound:
            music.ring_tone(1200)
        else:
            music.stop_all_sounds()
        tone_on = should_sound
    if state == "ALARM" and RADIO_ENABLED and now >= next_radio:
        radio.send_string("ALARM")
        next_radio = now + 1000
    basic.pause(LOOP_MS)


if RADIO_ENABLED:
    radio.set_group(RADIO_GROUP)
    radio.set_transmit_power(4)
# Prime the light sensor before calibration.
input.light_level()
basic.forever(run_tick)
