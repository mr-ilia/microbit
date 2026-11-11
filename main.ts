//  MISSION IMPOSSIBLE: MUSEUM BOX - MakeCode Python
//  A: change mode while disarmed. B: arm, cancel or reset.
//  Close the box during the 5-second countdown, then keep it still.
//  ---------- CHANGE THESE SETTINGS ----------
let MODE = "BOTH"
//  "LIGHT", "MOTION", or "BOTH" (light OR motion)
let LIGHT_THRESHOLD = 50
//  0-255. Trigger above this light level.
let MOTION_THRESHOLD = 150
//  milli-g. Trigger above this axis change.
let CONFIRM_MS = 100
//  Trigger must remain true for this long.
let SOUND_ENABLED = true
//  V2 speaker; V1 can use a P0/GND speaker.
let RADIO_ENABLED = false
//  Optional: needs a MakeCode radio receiver.
let RADIO_GROUP = 8
//  ------------------------------------------
let ARM_DELAY_MS = 5000
let CALIBRATION_MS = 1000
let LOOP_MS = 20
let mode = MODE
let state = "DISARMED"
let note = ""
let baseline = [0, 0, 0]
let total = [0, 0, 0]
let low = [0, 0, 0]
let high = [0, 0, 0]
let samples = 0
let brightest = 0
let since = 0
let candidate = -1
let shown = ""
let was_a = false
let was_b = false
let alarm_since = 0
let next_radio = 0
let tone_on = false
function alarm_rule(selected_mode: string, light_alarm: boolean, motion_alarm: boolean): boolean {
    //  The Boolean logic for this lesson:
    if (selected_mode == "LIGHT") {
        return light_alarm
    }
    
    if (selected_mode == "MOTION") {
        return motion_alarm
    }
    
    return light_alarm || motion_alarm
}

function motion_change(axes: number[]): number {
    //  Compare each axis with the fixed position saved during calibration.
    //  This detects tilting as well as shaking.
    return Math.max(Math.abs(axes[0] - baseline[0]), Math.max(Math.abs(axes[1] - baseline[1]), Math.abs(axes[2] - baseline[2])))
}

function update_alarm(now: number, a: boolean, b: boolean, light: number, axes: number[]) {
    let spread: number;
    let light_alarm: boolean;
    let motion_alarm: boolean;
    let trigger: boolean;
    
    
    //  B has priority: resetting the alarm cannot trigger it again.
    if (b) {
        note = ""
        candidate = -1
        if (state == "DISARMED") {
            state = "COUNTDOWN"
            since = now
        } else {
            state = "DISARMED"
        }
        
        return
    }
    
    if (state == "DISARMED") {
        if (a) {
            if (mode == "LIGHT") {
                mode = "MOTION"
            } else if (mode == "MOTION") {
                mode = "BOTH"
            } else {
                mode = "LIGHT"
            }
            
            note = ""
        }
        
        return
    }
    
    if (state == "COUNTDOWN") {
        if (now - since >= ARM_DELAY_MS) {
            state = "CALIBRATING"
            since = now
            total = [0, 0, 0]
            low = [32767, 32767, 32767]
            high = [-32767, -32767, -32767]
            samples = 0
            brightest = 0
        }
        
        return
    }
    
    if (state == "CALIBRATING") {
        samples += 1
        brightest = Math.max(brightest, light)
        for (let i = 0; i < 3; i++) {
            total[i] += axes[i]
            low[i] = Math.min(low[i], axes[i])
            high[i] = Math.max(high[i], axes[i])
        }
        if (now - since >= CALIBRATION_MS) {
            spread = Math.max(high[0] - low[0], Math.max(high[1] - low[1], high[2] - low[2]))
            if (mode != "LIGHT" && spread > MOTION_THRESHOLD) {
                state = "DISARMED"
                note = "STILL"
            } else if (mode != "MOTION" && brightest > LIGHT_THRESHOLD) {
                state = "DISARMED"
                note = "DARK"
            } else {
                for (let j = 0; j < 3; j++) {
                    baseline[j] = Math.floor(total[j] / samples)
                }
                state = "ARMED"
                candidate = -1
            }
            
        }
        
        return
    }
    
    if (state == "ARMED") {
        light_alarm = light > LIGHT_THRESHOLD
        motion_alarm = motion_change(axes) > MOTION_THRESHOLD
        trigger = alarm_rule(mode, light_alarm, motion_alarm)
        if (!trigger) {
            candidate = -1
        } else if (candidate < 0) {
            candidate = now
        } else if (now - candidate >= CONFIRM_MS) {
            state = "ALARM"
        }
        
    }
    
}

//  The alarm stays latched even when the box becomes dark/still again.
if (RADIO_ENABLED) {
    radio.setGroup(RADIO_GROUP)
    radio.setTransmitPower(4)
}

//  Prime the light sensor before calibration.
input.lightLevel()
basic.forever(function run_tick() {
    
    let now = input.runningTime()
    let a_down = input.buttonIsPressed(Button.A)
    let b_down = input.buttonIsPressed(Button.B)
    let old_state = state
    update_alarm(now, a_down && !was_a, b_down && !was_b, input.lightLevel(), [input.acceleration(Dimension.X), input.acceleration(Dimension.Y), input.acceleration(Dimension.Z)])
    was_a = a_down
    was_b = b_down
    if (state == "ALARM" && old_state != "ALARM") {
        alarm_since = now
        next_radio = now
    }
    
    //  One short display update keeps B responsive in every state.
    let symbol = ""
    if (state == "DISARMED") {
        if (note != "") {
            symbol = note.charAt(Math.idiv(now, 250) % (note.length + 2))
        } else if (mode == "LIGHT") {
            symbol = "L"
        } else if (mode == "MOTION") {
            symbol = "M"
        } else {
            symbol = "O"
        }
        
    } else if (state == "COUNTDOWN") {
        symbol = "" + Math.max(1, Math.ceil((ARM_DELAY_MS - (now - since)) / 1000))
    } else if (state == "ARMED") {
        symbol = "."
    } else if (state == "ALARM" && Math.idiv(now - alarm_since, 250) % 2 == 0) {
        symbol = "X"
    }
    
    if (symbol != shown) {
        basic.clearScreen()
        if (symbol == ".") {
            led.plotBrightness(2, 2, 25)
        } else if (symbol != "") {
            basic.showString(symbol, 1)
        }
        
        shown = symbol
    }
    
    let should_sound = state == "ALARM" && SOUND_ENABLED && (now - alarm_since) % 500 < 180
    if (should_sound != tone_on) {
        if (should_sound) {
            music.ringTone(1200)
        } else {
            music.stopAllSounds()
        }
        
        tone_on = should_sound
    }
    
    if (state == "ALARM" && RADIO_ENABLED && now >= next_radio) {
        radio.sendString("ALARM")
        next_radio = now + 1000
    }
    
    basic.pause(LOOP_MS)
})
