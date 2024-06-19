from flask import Flask, request, render_template
import RPi.GPIO as GPIO
import time

app = Flask(__name__)

# Pin definitions
STEP_PIN = 17
DIR_PIN = 18
LIMIT_SWITCH_PIN = 27

# Motor specifications
STEPS_PER_REV = 200
LEAD_SCREW_PITCH = 2  # mm per revolution

# Calculate steps per mm
STEPS_PER_MM = STEPS_PER_REV / LEAD_SCREW_PITCH
STEPS_PER_0_1MM = STEPS_PER_MM / 10

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(LIMIT_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def move_stepper(steps, direction, delay=0.001):
    # Set direction
    GPIO.output(DIR_PIN, direction)
    
    # Move stepper
    for _ in range(steps):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(delay)

def home_stepper():
    # Set direction to backward
    GPIO.output(DIR_PIN, GPIO.LOW)
    
    # Move stepper until limit switch is triggered
    while GPIO.input(LIMIT_SWITCH_PIN) == GPIO.HIGH:
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(0.001)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def move():
    distance = float(request.form['distance'])
    direction = request.form['direction']
    
    steps = int(distance * STEPS_PER_MM)
    
    if direction == 'forward':
        dir_value = GPIO.HIGH
    else:
        dir_value = GPIO.LOW
    
    move_stepper(steps, dir_value)
    
    return f'Moved {distance} mm {"forward" if direction == "forward" else "backward"}'

@app.route('/home', methods=['POST'])
def home():
    home_stepper()
    return 'Stepper motor homed successfully'

@app.route('/move_step', methods=['POST'])
def move_step():
    step_direction = request.form['step_direction']
    action = request.form['action']
    
    if step_direction == 'forward':
        dir_value = GPIO.HIGH
    else:
        dir_value = GPIO.LOW
    
    if action == 'Move 1 Step':
        steps = 1
    elif action == 'Move 0.1 mm':
        steps = int(STEPS_PER_0_1MM)
    
    move_stepper(steps, dir_value)
    
    return f'{action} {"forward" if step_direction == "forward" else "backward"}'

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()