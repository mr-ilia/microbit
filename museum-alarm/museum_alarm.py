# MISSION IMPOSSIBLE: MUSEUM BOX - BBC micro:bit MicroPython
# Open this file in https://python.microbit.org/ (not MakeCode Python).
# A: change mode while disarmed. B: arm, or cancel/reset at any time.
# After B: place board and close box during 5-second countdown; leave still.

# ---------- CHANGE THESE SETTINGS ----------
MODE = "BOTH"             # "LIGHT", "MOTION", or "BOTH" (light OR motion)
LIGHT_THRESHOLD = 50      # 0-255. Alarm if light is GREATER than this.
MOTION_THRESHOLD = 150    # milli-g. Alarm if any axis changes MORE than this.
CONFIRM_MS = 100          # Trigger must remain true for this long.
SOUND_ENABLED = True      # V2: built-in speaker. V1: optional P0/GND speaker.
RADIO_ENABLED = False     # Later extension: use museum_receiver.py too.
RADIO_GROUP = 8           # 0-255; use a different group for each team.
# ------------------------------------------
ARM_DELAY_MS = 5000
CALIBRATION_MS = 1000
LOOP_MS = 20
MODES = ("LIGHT", "MOTION", "BOTH")


def alarm_rule(mode, light_alarm, motion_alarm):
    # The important Boolean logic for this lesson:
    if mode == "LIGHT":
        return light_alarm
    if mode == "MOTION":
        return motion_alarm
    return light_alarm or motion_alarm


def motion_change(axes, baseline):
    # Compare EACH axis with the fixed position saved when we armed.
    # Comparing total acceleration alone would miss many tilts.
    return max(abs(axes[0] - baseline[0]),
               abs(axes[1] - baseline[1]),
               abs(axes[2] - baseline[2]))


class MuseumAlarm:
    def __init__(self, mode=MODE):
        if mode not in MODES:
            raise ValueError("MODE must be LIGHT, MOTION or BOTH")
        self.mode = mode
        self.state = "DISARMED"
        self.note = ""
        self.baseline = (0, 0, 0)
        self.since = 0
        self.candidate = None

    def update(self, now, a, b, light, axes):
        # Read B FIRST: a reset cannot itself trigger the motion alarm.
        if b:
            self.note = ""
            self.candidate = None
            if self.state == "DISARMED":
                self.state = "COUNTDOWN"
                self.since = now
            else:
                self.state = "DISARMED"
            return

        if self.state == "DISARMED":
            if a:
                self.mode = MODES[(MODES.index(self.mode) + 1) % 3]
                self.note = ""
            return

        if self.state == "COUNTDOWN":
            if now - self.since >= ARM_DELAY_MS:
                self.state = "CALIBRATING"
                self.since = now
                self.total = [0, 0, 0]
                self.low = [32767, 32767, 32767]
                self.high = [-32767, -32767, -32767]
                self.samples = 0
                self.brightest = 0
            return

        if self.state == "CALIBRATING":
            self.samples += 1
            self.brightest = max(self.brightest, light)
            for i in range(3):
                self.total[i] += axes[i]
                self.low[i] = min(self.low[i], axes[i])
                self.high[i] = max(self.high[i], axes[i])
            if now - self.since >= CALIBRATION_MS:
                if self.mode != "LIGHT" and max(self.high[i] - self.low[i] for i in range(3)) > MOTION_THRESHOLD:
                    self.state, self.note = "DISARMED", "STILL"
                elif self.mode != "MOTION" and self.brightest > LIGHT_THRESHOLD:
                    self.state, self.note = "DISARMED", "DARK"
                else:
                    self.baseline = tuple(v // self.samples for v in self.total)
                    self.state = "ARMED"
                    self.candidate = None
            return

        if self.state == "ARMED":
            light_alarm = light > LIGHT_THRESHOLD
            motion_alarm = motion_change(axes, self.baseline) > MOTION_THRESHOLD
            trigger = alarm_rule(self.mode, light_alarm, motion_alarm)
            if not trigger:
                self.candidate = None
            elif self.candidate is None:
                self.candidate = now
            elif now - self.candidate >= CONFIRM_MS:
                self.state = "ALARM"
        # ALARM stays latched even if the box becomes dark/still again.


def run():
    from microbit import display, Image, button_a, button_b
    from microbit import accelerometer, running_time, sleep
    if SOUND_ENABLED:
        import music
    if RADIO_ENABLED:
        import radio
        radio.config(group=RADIO_GROUP, power=4, length=32)
        radio.on()

    alarm = MuseumAlarm()
    shown = None
    next_beep = 0
    next_radio = 0
    # Prime the light sensor before setup/calibration.
    display.read_light_level()

    while True:
        now = running_time()
        # Consume BOTH events, even when A is ignored while armed.
        b = button_b.was_pressed()
        a = button_a.was_pressed()
        old_state = alarm.state
        alarm.update(now, a, b, display.read_light_level(),
                     accelerometer.get_values())

        if old_state == "ALARM" and alarm.state != "ALARM":
            if SOUND_ENABLED:
                music.stop()

        state = alarm.state
        if state == "DISARMED":
            symbol = ("L", "M", "O")[MODES.index(alarm.mode)]
            key = (state, symbol, alarm.note)
            if key != shown:
                if alarm.note:
                    display.scroll(alarm.note, delay=100, wait=False, loop=True)
                else:
                    display.show(symbol)
                shown = key
        elif state == "COUNTDOWN":
            digit = max(1, (ARM_DELAY_MS - (now - alarm.since) + 999) // 1000)
            key = (state, digit)
            if key != shown:
                display.show(str(digit))
                shown = key
        elif state == "CALIBRATING":
            if shown != state:
                display.clear()
                shown = state
        elif state == "ARMED":
            if shown != state:
                display.clear()
                display.set_pixel(2, 2, 1)  # One dim dot: armed.
                shown = state
        else:  # Latched alarm: flash X without blocking button checks.
            key = (state, (now // 250) % 2)
            if key != shown:
                display.show(Image.NO if key[1] == 0 else Image())
                shown = key
            if old_state != "ALARM":
                next_beep = next_radio = now
            if SOUND_ENABLED and now >= next_beep:
                music.pitch(1200, 180, wait=False)
                next_beep = now + 500
            if RADIO_ENABLED and now >= next_radio:
                radio.send("ALARM")
                next_radio = now + 1000
        sleep(LOOP_MS)


if __name__ == "__main__":
    run()
