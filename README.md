# micro:bit classroom projects

## Mission Impossible: Museum Box

Build a museum alarm that reacts when someone opens or moves the box.

**[Open the museum alarm code](museum-alarm/museum_alarm.py)**  
**[Open the plain-text code](https://raw.githubusercontent.com/iliavialyh/microbit/main/museum-alarm/museum_alarm.py)**

### Copy the code

1. Open the code link above and use the **Copy raw file** button above the code. Alternatively, open the plain-text link, select all, and copy.
2. Open the [micro:bit Python Editor](https://python.microbit.org/).
3. Replace the starter code with the copied program, keeping its indentation.
4. Transfer the program to your micro:bit using your usual classroom method.

This program uses **BBC micro:bit MicroPython**, not MakeCode Python.

### Use your alarm

- Press **A** while disarmed to change mode: **L** = light, **M** = motion, **O** = light **OR** motion.
- Press **B** to arm. Put the micro:bit in the box and close it during the five-second countdown.
- Leave the box still for one more second while the sensor calibrates. A dim centre dot means it is armed.
- Open or move the box to trigger the alarm. Press **B** to stop/reset it.
- If **DARK** appears, close the box more fully and press B to try again. If **STILL** appears, keep the box still during calibration and try again.

### Change the settings

Edit the settings near the top of `museum_alarm.py`:

| Setting | Starting value | What it controls |
| --- | --- | --- |
| `MODE` | `"BOTH"` | `"LIGHT"`, `"MOTION"`, or `"BOTH"` |
| `LIGHT_THRESHOLD` | `50` | A higher light reading triggers the light alarm. |
| `MOTION_THRESHOLD` | `150` | A larger change on any acceleration axis triggers the motion alarm. |
| `SOUND_ENABLED` | `True` | Sound on/off; V2 has a built-in speaker. |

In **BOTH** mode, either sensor can trigger the alarm: `light_alarm or motion_alarm`.

Radio is disabled for this lesson. Leave `RADIO_ENABLED = False`; the optional receiver program is a later extension and is not included here.

The Python file is an unchanged copy of the supplied classroom program.
