from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
import random
from os import system
from keyboard import is_pressed
from time import sleep

# Clear the terminal screen (for macOS/Linux)
system('clear')

# Configuration and Setup
def get_meeting_details():
    """Prompt the user for meeting ID, passcode, and bot count."""
    meetingID = input('Meeting ID: ')
    meetingPasscode = input('Meeting Passcode: ')
    numberOfBots = int(input('Bot(s) Number: '))
    customName = input('Name (Leave blank for Random name): ')
    return meetingID, meetingPasscode, numberOfBots, customName

# Load meeting details
meetingID, meetingPasscode, numberOfBots, customName = get_meeting_details()
system('clear')

# Load random names
with open('names.txt', 'r') as file:
    names = file.read().split('\n')

# Set up Chrome options
def configure_chrome_options():
    """Configure Chrome options for the bots."""
    options = Options()
    options.add_argument('--log-level=3')
    options.add_argument("--disable-infobars")
    options.add_argument("start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--mute-audio")
    options.add_argument("--headless")
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.media_stream_mic": 2,
        "profile.default_content_setting_values.media_stream_camera": 2
    })
    return options

options = configure_chrome_options()

# Create and join bots
def create_bot():
    """Initialize a bot with the specified Chrome options."""
    service = Service('/usr/local/bin/chromedriver')  # Path to chromedriver
    return webdriver.Chrome(service=service, options=options)

def safe_click(driver, by, value, retries=3):
    """Attempt to click an element, with retries and error handling for common exceptions."""
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((by, value)))
            ActionChains(driver).move_to_element(element).perform()  # Scroll to element
            element.click()
            return True
        except (ElementClickInterceptedException, ElementNotInteractableException) as e:
            print(f"Click intercepted or not interactable, retrying... Attempt {attempt + 1}/{retries}")
            sleep(1)  # Brief wait before retrying
        except (NoSuchElementException, TimeoutException):
            print(f"Element not found or not clickable: {value}")
            return False
    print(f"Failed to click element after {retries} attempts: {value}")
    return False

def join_meeting(driver, meetingID, meetingPasscode, baseName):
    """Join the meeting with the specified details."""
    driver.get(f'https://zoom.us/wc/join/{meetingID}')

    # Wait for the name input field to be present and enter the name
    try:
        name_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'input-for-name'))
        )
        name_input.send_keys(baseName)
    except (NoSuchElementException, TimeoutException):
        print("Name input field not found.")
        driver.quit()
        return

    # Wait for the passcode input field and enter the passcode
    try:
        passcode_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'input-for-pwd'))
        )
        passcode_input.send_keys(meetingPasscode)
    except (NoSuchElementException, TimeoutException):
        print("Passcode input field not found.")
        driver.quit()
        return

    # Click the join button
    if not safe_click(driver, By.CLASS_NAME, 'preview-join-button'):
        driver.quit()
        return

    # Click the "Join Audio by Computer" button
    if not safe_click(driver, By.CLASS_NAME, 'join-audio-by-voip__join-btn'):
        driver.quit()
        return

# Launching bots
drivers = []
print('Please ignore any warnings. Bots are joining the meeting...')
for _ in range(numberOfBots):
    driver = create_bot()
    drivers.append(driver)
    # Use custom name or random name from the list
    baseName = customName if customName else random.choice(names)
    join_meeting(driver, meetingID, meetingPasscode, baseName)
    system('clear')

print('All bot(s) have joined!\nPress Alt+Ctrl+Shift+E to exit all bots')

# Exit all bots
def exit_bots():
    """Exit all bots when the specified key combination is pressed."""
    while True:
        if is_pressed('alt') and is_pressed('ctrl') and is_pressed('shift') and (is_pressed('e') or is_pressed('E')):
            system('clear')
            for i, driver in enumerate(drivers):
                print(f'Exiting Bot Number {i + 1}')
                sleep(0.075)
                driver.close()
            print('All bots exited. Please manually exit any remaining windows if needed.')
            break

# Wait for user to quit bots
exit_bots()