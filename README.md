# Mission Impossible: Museum Box

A micro:bit alarm that reacts when someone opens or moves the museum box.

## Import in the micro:bit app or MakeCode

1. Open **Create Code / MakeCode**, then **Import → Import URL**.
2. Paste this repository link:

   **https://github.com/mr-ilia/microbit**

3. Choose **Go ahead!**. The museum alarm opens in **Python**.
4. Replace **both `None` placeholders** for `LIGHT_THRESHOLD` and `MOTION_THRESHOLD` near the top of the Python code with your own numbers. Each says `(you need to work it out yourself!)`.
5. Choose **Download** and transfer to your micro:bit. Until both values are chosen, the program displays **SET THRESHOLDS** and does not arm.

Import the whole repository link above, rather than a link to an individual file. The project files at the top of this repository are for **MakeCode Python**, the editor used by the micro:bit app.

## Use your alarm

- Press **A** while disarmed to change mode: **L** = light, **M** = motion, **O** = light **OR** motion.
- Press **B** to arm. Place the micro:bit in the box and close it during the five-second countdown.
- Keep the box still for one more second while it calibrates. A dim centre dot means it is armed.
- Open or move the box to trigger the flashing, sounding alarm. Press **B** to stop/reset it. B also cancels the countdown or calibration.
- If **DARK** appears letter by letter, close the box more fully and press B again. If **STILL** appears, keep the box still during calibration and try again.

## Change the settings

Edit the settings near the top of [main.py](main.py), or directly in MakeCode's Python editor:

| Setting | Starting value | What it controls |
| --- | --- | --- |
| `MODE` | `"BOTH"` | `"LIGHT"`, `"MOTION"`, or `"BOTH"` |
| `LIGHT_THRESHOLD` | You need to work it out yourself! | Light above this value triggers the light alarm. |
| `MOTION_THRESHOLD` | You need to work it out yourself! | Change on any acceleration axis above this value triggers the motion alarm. |
| `CONFIRM_MS` | `100` | How long the trigger must stay true before the alarm sounds. |
| `SOUND_ENABLED` | `True` | Sound on/off; V2 has a built-in speaker, V1 can use P0/GND. |

In **BOTH** mode, either sensor can trigger the alarm: `light_alarm or motion_alarm`.

Radio is disabled for this lesson. Leave `RADIO_ENABLED = False`. The optional radio extension sends the string `ALARM` to a **MakeCode** receiver on group 8; a receiver is not included here. It does not use the original MicroPython radio packet format.

## MicroPython version

A MicroPython version with the same two threshold placeholders is available at [museum-alarm/museum_alarm.py](museum-alarm/museum_alarm.py), with a [plain-text copy](https://raw.githubusercontent.com/mr-ilia/microbit/main/museum-alarm/museum_alarm.py).

Replace both `None` placeholders with your chosen numbers and use that file in the separate [micro:bit Python Editor](https://python.microbit.org/). It uses different APIs from MakeCode Python and should not be pasted into the app's MakeCode editor.
