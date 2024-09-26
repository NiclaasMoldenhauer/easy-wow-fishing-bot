import pyautogui
import time
import random
from pynput.mouse import Button, Controller
import os
import numpy as np
from PIL import Image
from collections import deque

def find_file(filename, search_path):
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # Go one level up

# Try to find bait.png
BAIT_IMAGE = find_file("bait.png", project_root)
if BAIT_IMAGE is None:
    raise FileNotFoundError(f"Could not find bait.png in or above {script_dir}")

FISHING_BUTTON = "mouse5"  # Represents the 5th mouse button
INTERACT_BUTTON = Button.x1  # Represents the 4th mouse button for interaction
TUNE_BAIT_MOUSE_UNDER_PX = 35
# EDGE_RESET = 10, 10
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

def click_interact_button():
    print("Clicking interact button (Mouse4)")
    mouse.press(INTERACT_BUTTON)
    time.sleep(0.1)  # Short delay to ensure the click registers
    mouse.release(INTERACT_BUTTON)

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
    
    # print(f"Current movement: {current_movement:.2f}, Threshold: {threshold:.2f}, Sustained Threshold: {sustained_threshold:.2f}")
    
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

print(f"Script directory: {script_dir}")
print(f"Project root directory: {project_root}")
print(f"Looking for bait image at: {BAIT_IMAGE}")
print(f"Current working directory: {os.getcwd()}")
print("Files in the current directory:")
for file in os.listdir():
    print(f" - {file}")

time.sleep(ACTIVE_AFTER)

while True:
    print("\n--- Starting new fishing cycle ---")
    time.sleep(0.25 + random.uniform(0, 1.5))

    # 10% Chance to press "space"
    chance = random.randint(0, 100)
    if chance <= 10:
        print("Pressing space")
        pyautogui.press("space")
        time.sleep(2)

    cast_attempts = 0
    bobber_found = False

    while cast_attempts < MAX_CAST_ATTEMPTS and not bobber_found:
        click_fishing_button()
        cast_attempts += 1
        print(f"Cast attempt {cast_attempts}")

        # Resetting the mouse's pos
        # pyautogui.moveTo(*EDGE_RESET)
        # print(f"Reset mouse position to {EDGE_RESET}")
        
        time.sleep(3)  # Wait for the bobber to appear
        
        bobber = find_on_screen(BAIT_IMAGE)
        if bobber is not None:
            bobber_found = True
            break
        
        print("Couldn't find the bobber. Trying again.")
        time.sleep(1)  # Short delay before next attempt

    if not bobber_found:
        print("Failed to find bobber after maximum attempts. Restarting cycle.")
        continue

    fishing = True
    movement_history = deque(maxlen=HISTORY_SIZE)
    last_large_movement_time = 0
    
    bobber_region = get_bobber_region(bobber)
    pyautogui.moveTo(bobber.x, bobber.y + TUNE_BAIT_MOUSE_UNDER_PX)
    print(f"Moved mouse to bobber position: ({bobber.x}, {bobber.y + TUNE_BAIT_MOUSE_UNDER_PX})")
    
    initial_image = pyautogui.screenshot(region=bobber_region)
    start_time = time.time()
    
    while fishing and time.time() - start_time < 23:  # Wait up to 23 seconds for a bite
        time.sleep(DETECTION_INTERVAL)
        current_image = pyautogui.screenshot(region=bobber_region)
        
        movement = calculate_movement(initial_image, current_image)
        movement_history.append(movement)
        
        fish_bite, last_large_movement_time = detect_fish_bite(movement_history, last_large_movement_time)
        if fish_bite:
            click_interact_button()
            print("Waiting 2 seconds before next cast")
            time.sleep(2)  # Wait for 2 seconds before casting again
            fishing = False
            break
        
        initial_image = current_image  # Update the reference image
    
    if fishing:
        print("No fish caught within 30 seconds. Restarting cycle.")

    print("Waiting 1 second before next cast")
    time.sleep(1)  # Short delay before next cast