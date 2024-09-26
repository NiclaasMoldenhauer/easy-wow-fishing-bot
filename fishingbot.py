import PySimpleGUI as sg
import pyautogui
import time
import random
from pynput.mouse import Button, Controller
import numpy as np
from PIL import Image
from collections import deque
import sys
import os

def find_file(filename, search_path):
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # Go one level up

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

BAIT_IMAGE = resource_path("bait.png")
print(f"Attempting to load bait image from: {BAIT_IMAGE}")

FISHING_BUTTON = "mouse5"  # Represents the 5th mouse button
INTERACT_BUTTON = Button.x1  # Represents the 4th mouse button for interaction
TUNE_BAIT_MOUSE_UNDER_PX = 35
ACTIVE_AFTER = 3
CONFIDENCE = 0.5
MAX_CAST_ATTEMPTS = 3  # Maximum number of casting attempts before resetting
INTERACTION_DELAY_MIN = 0.4  # Minimum delay before interaction
INTERACTION_DELAY_MAX = 0.8  # Maximum delay before interaction
MOVEMENT_THRESHOLD = 2.5  # Increased threshold for higher specificity
SUSTAINED_MOVEMENT_THRESHOLD = 2  # Increased threshold for sustained movement
DETECTION_INTERVAL = 0.05  # Keep this value for frequent checks
BOBBER_REGION_SIZE = (60, 60)  # Keep this value
HISTORY_SIZE = 35  # Increased history size for better average calculation
SUSTAINED_MOVEMENT_COUNT = 3  # Increased count for more reliable sustained movement detection
COOLDOWN_PERIOD = 1  # Cooldown period after a large movement to prevent false positives

mouse = Controller()

def find_on_screen(image):
    max_attempts = 8
    attempts = 0
    while attempts < max_attempts:
        try:
            loc = pyautogui.locateOnScreen(image, confidence=CONFIDENCE)
            if loc is None:
                print(f"Attempt {attempts + 1}: Cannot find the image: {image}")
                attempts += 1
                time.sleep(1)  # Wait a bit before trying again
                continue
            cp_loc = pyautogui.center(loc)
            print(f"Found bait at position: {cp_loc}")
            return cp_loc
        except Exception as e:
            print(f"Attempt {attempts + 1}: Error finding image: {e}")
            attempts += 1
            time.sleep(1)  # Wait a bit before trying again
    return None

def click_interact_button():
    delay = random.uniform(INTERACTION_DELAY_MIN, INTERACTION_DELAY_MAX)
    print(f"Fish bite detected! Waiting {delay:.2f} seconds before interaction.")
    time.sleep(delay)
    print("Clicking interact button (Mouse4)")
    mouse.press(INTERACT_BUTTON)
    time.sleep(0.1)  # Short delay to ensure the click registers
    mouse.release(INTERACT_BUTTON)

def click_fishing_button():
    print("Clicking fishing button (Mouse5)")
    if FISHING_BUTTON == "mouse5":
        mouse.press(Button.x2)
        mouse.release(Button.x2)
    else:
        pyautogui.press(FISHING_BUTTON)

def get_bobber_region(bobber_pos):
    x, y = bobber_pos
    width, height = BOBBER_REGION_SIZE
    left = max(x - width // 2, 0)
    top = max(y - height // 2, 0)
    return (left, top, width, height)

def calculate_movement(initial_image, current_image):
    diff = np.abs(np.array(initial_image) - np.array(current_image))
    return np.sum(diff)

def detect_fish_bite(movement_history, last_large_movement_time):
    if len(movement_history) < HISTORY_SIZE:
        return False, last_large_movement_time
    
    mean_movement = np.mean(movement_history)
    std_movement = np.std(movement_history)
    threshold = mean_movement + (MOVEMENT_THRESHOLD * std_movement)
    sustained_threshold = mean_movement + (SUSTAINED_MOVEMENT_THRESHOLD * std_movement)
    
    current_movement = movement_history[-1]
    current_time = time.time()
    
    # Check for sudden large movement
    if current_movement > threshold:
        if current_time - last_large_movement_time > COOLDOWN_PERIOD:
            print(f"Large movement detected! {current_movement:.2f} > {threshold:.2f}")
            return True, current_time
        else:
            print("Large movement ignored due to cooldown")
    
    # Check for sustained smaller movement
    recent_movements = list(movement_history)[-SUSTAINED_MOVEMENT_COUNT:]
    if all(move > sustained_threshold for move in recent_movements):
        print(f"Sustained movement detected! All recent movements > {sustained_threshold:.2f}")
        return True, current_time
    
    return False, last_large_movement_time

def main():
    layout = [
        [sg.Text("WoW Fishing Bot by Rejoove", font=('Helvetica', 16))],
        [sg.Text("Status: "), sg.Text("Idle", key="-STATUS-")],
        [sg.Button("Start"), sg.Button("Stop"), sg.Button("Exit")]
    ]

    window = sg.Window("WoW Fishing Bot by Rejoove", layout)

    fishing_active = False
    state = "IDLE"
    start_time = 0
    cast_attempts = 0
    bobber = None
    movement_history = deque(maxlen=HISTORY_SIZE)
    last_large_movement_time = 0
    initial_image = None
    
    while True:
        event, values = window.read(timeout=100)  # Reduced timeout for more responsiveness
        
        if event == sg.WINDOW_CLOSED or event == "Exit":
            break
        elif event == "Start" and state == "IDLE":
            fishing_active = True
            state = "START_FISHING"
            window["-STATUS-"].update("Starting fishing")
        elif event == "Stop":
            fishing_active = False
            state = "IDLE"
            window["-STATUS-"].update("Stopped")

        if fishing_active:
            if state == "START_FISHING":
                window["-STATUS-"].update("Starting new fishing cycle")
                time.sleep(0.25 + random.uniform(0, 1.5))
                
                # 10% Chance to press "space"
                if random.randint(0, 100) <= 10:
                    window["-STATUS-"].update("Pressing space")
                    pyautogui.press("space")
                    time.sleep(2)
                
                state = "CAST_LINE"
                cast_attempts = 0
                
            elif state == "CAST_LINE":
                if cast_attempts < MAX_CAST_ATTEMPTS:
                    window["-STATUS-"].update(f"Cast attempt {cast_attempts + 1}")
                    click_fishing_button()
                    cast_attempts += 1
                    state = "FIND_BOBBER"
                    start_time = time.time()
                else:
                    window["-STATUS-"].update("Failed to find bobber. Restarting cycle.")
                    state = "START_FISHING"
                
            elif state == "FIND_BOBBER":
                if time.time() - start_time > 3:  # Wait up to 3 seconds for bobber
                    bobber = find_on_screen(BAIT_IMAGE)
                    if bobber:
                        window["-STATUS-"].update(f"Found bobber at {bobber}")
                        pyautogui.moveTo(bobber.x, bobber.y + TUNE_BAIT_MOUSE_UNDER_PX)
                        state = "WATCH_BOBBER"
                        start_time = time.time()
                        movement_history.clear()
                        bobber_region = get_bobber_region(bobber)
                        initial_image = pyautogui.screenshot(region=bobber_region)
                    else:
                        state = "CAST_LINE"
                
            elif state == "WATCH_BOBBER":
                if time.time() - start_time < 23:  # Watch for up to 23 seconds
                    current_image = pyautogui.screenshot(region=bobber_region)
                    movement = calculate_movement(initial_image, current_image)
                    movement_history.append(movement)
                    
                    fish_bite, last_large_movement_time = detect_fish_bite(movement_history, last_large_movement_time)
                    if fish_bite:
                        window["-STATUS-"].update("Fish bite detected!")
                        click_interact_button()
                        window["-STATUS-"].update("Waiting 2 seconds before next cast")
                        time.sleep(2)
                        state = "START_FISHING"
                    
                    initial_image = current_image
                else:
                    window["-STATUS-"].update("No fish caught within 23 seconds. Restarting cycle.")
                    state = "START_FISHING"

        window.refresh()

    window.close()

if __name__ == "__main__":
    main()