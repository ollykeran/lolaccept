import cv2
import os
import numpy as np
import pyautogui
import pygetwindow as gw
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import time
import keyboard 
import logging
import queue
import requests

# Initialize global variables with default values
pick = True
ban = True
accept = False
pick_choice = ""
ban_choice = ""

sleepTime = 1
inputDelay = 1 

# Set the path to images
images = {
    "accept": "images/accept.png",
    "pick": "images/pick.png",
    "ban": "images/ban.png"
}

# Tolerance level for matching
tolerance = 0.8  

# Coordinates relative to the window
coordinates = {
    "search_bar": (950, 130),
    "champ": (450, 180),
    "button": (800, 750),
    "accept": (800, 700),
    "bans" : (1600, 100)
}

def get_latest_version():
    version_url = "https://ddragon.leagueoflegends.com/api/versions.json"
    response = requests.get(version_url)
    if response.status_code == 200:
        versions = response.json()
        return versions[0]  # return the first version

def get_champion_names(version):
    champion_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
    response = requests.get(champion_url)
    if response.status_code == 200:
        champion_data = response.json()
        champions = champion_data.get('data', {})
        # Extract only the names of the champions
        return [champ['name'] for champ in champions.values()]
    else:
        return []

def clean_champion_name(name):
    # Wukong.png does not exist?
    # Convert to lowercase
    name = name.lower()
    # for Nunu&Willump the png is called Nunu 
    if '&' in name:
        name = name.split('&')[0]
    # for renata its just called "renata"
    if "renata" in name: 
        name = name.split(' ')[0]
    name = name.replace(' ', '').replace("'", '').replace('.', '')
    return name
    

def download_champion_images(version, save_directory):
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
        
    for champ_name in champion_names:
        cleaned_name = clean_champion_name(champ_name)
        image_path = os.path.join(save_directory, f"{cleaned_name}.png")
        
        if os.path.exists(image_path):
            logger.debug(f"Image already exists for {cleaned_name}")
            continue
        
        image_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{cleaned_name}.png"
        response = requests.get(image_url)
        
        if response.status_code == 200:
            with open(image_path, 'wb') as file:
                file.write(response.content)
            logger.debug(f"Downloaded champion image {cleaned_name}")
        else:
            logger.debug(f"Failed to download {cleaned_name}, response code: {response.status_code}")
        
        # Add a delay to avoid throttling
        time.sleep(sleepTime)

def activate_window(title):
    """Activate the window with the given title."""
    try:
        window = gw.getWindowsWithTitle(title)[0]
        window.activate()
        window.maximize()  # Optionally maximize the window
        window.restore()  # Restore the window if minimized
        time.sleep(1)  # Wait for the window to be activated
    except IndexError:
        logger.error(f"Window with title '{title}' not found.")
        exit()

def image_search(image_file, window_title):
    """Search for an image within the specified window."""
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        region = (window.left, window.top, window.width, window.height)

        screenshot = pyautogui.screenshot(region=region)
        screenshot_np = np.array(screenshot)
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)
        
        if template is None:
            raise FileNotFoundError(f"Template image not found: {image_file}")

        w, h = template.shape[::-1]
        result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= tolerance)
        
        for pt in zip(*loc[::-1]):
            return (pt[0] + window.left + w // 2, pt[1] + window.top + h // 2)
        return None
    except Exception as e:
        logger.error(f"Error during image search: {e}")
        return None


def gui(champion_names):
    """Create and display a centered GUI window for user input."""
    
    def filter_combobox(event, combobox, all_values):
        # Get the current text from the combobox
        search_text = combobox.get()
        
        # Filter the options based on the current text
        filtered_options = [name for name in all_values if search_text.lower() in name.lower()]
        
        # Update the combobox options
        combobox['values'] = filtered_options
        # Optionally, set the cursor to the end of the input text
        combobox.icursor(tk.END)
        
    def on_focus(event):
        combobox = event.widget
        combobox.event_generate('<Down>')   
        
    def on_submit():
        global pick, ban, accept, pick_choice, ban_choice
        pick = pick_var.get()
        ban = ban_var.get()
        accept = accept_var.get()
        pick_choice = pick_choice_combobox.get()
        ban_choice = ban_choice_combobox.get()
        root.destroy()

    root = tk.Tk()
    root.title("Pick/Ban/Accept Selection")

    # Define the input fields and buttons

    # Pick Choice Combobox (with autocomplete)
    tk.Label(root, text="Pick Choice:").grid(row=0, column=0, padx=10, pady=10)
    pick_choice_combobox = ttk.Combobox(root, values=champion_names)
    pick_choice_combobox.grid(row=0, column=1, padx=10, pady=10)
    pick_choice_combobox.set('')  # Empty initial value
    pick_choice_combobox.bind('<KeyRelease>', lambda event: filter_combobox(event, pick_choice_combobox, champion_names))


    # Ban Choice Combobox (with autocomplete)
    tk.Label(root, text="Ban Choice:").grid(row=1, column=0, padx=10, pady=10)
    ban_choice_combobox = ttk.Combobox(root, values=champion_names)
    ban_choice_combobox.grid(row=1, column=1, padx=10, pady=10)
    ban_choice_combobox.set('')  # Empty initial value
    ban_choice_combobox.bind('<KeyRelease>', lambda event: filter_combobox(event, ban_choice_combobox, champion_names))

    # Pick Checkbox
    tk.Label(root, text="Pick").grid(row=2, column=0, padx=10, pady=10)
    pick_var = tk.BooleanVar(value=pick)
    tk.Checkbutton(root, variable=pick_var).grid(row=2, column=1, padx=10, pady=10)

    # Ban Checkbox
    tk.Label(root, text="Ban").grid(row=3, column=0, padx=10, pady=10)
    ban_var = tk.BooleanVar(value=ban)
    tk.Checkbutton(root, variable=ban_var).grid(row=3, column=1, padx=10, pady=10)

    # Accept Checkbox (disabled)
    tk.Label(root, text="Accept").grid(row=4, column=0, padx=10, pady=10)
    accept_var = tk.BooleanVar(value=accept)
    tk.Checkbutton(root, variable=accept_var, state=tk.DISABLED).grid(row=4, column=1, padx=10, pady=10)
    #, state=tk.DISABLED

    # Submit Button
    tk.Button(root, text="Submit", command=on_submit).grid(row=5, column=0, columnspan=2, pady=10)

    # Center the window on the screen
    root.update_idletasks()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    root.mainloop()

def search_and_click(image_key, input_text, window_title):
    """Search for an image and perform click actions."""
    logger.info(f"Looking for {images[image_key]} in window '{window_title}'")
    activate_window("League of Legends")
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        while True:
            if keyboard.is_pressed('esc'):  # Check for escape key
                logger.info("Escape key pressed. Exiting...")
                return

            location = image_search(images[image_key], window_title)
            if location:
                logger.debug(f"Found the image: {image_key}")

                # Convert relative coordinates to absolute coordinates
                abs_coords = {
                    name: (window.left + x, window.top + y)
                    for name, (x, y) in coordinates.items()
                }

                time.sleep(inputDelay)
                pyautogui.click(*abs_coords["search_bar"])
                time.sleep(inputDelay)
                # make sure previous input is cleared
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                pyautogui.write(input_text, interval=0.1)
                time.sleep(inputDelay)
                pyautogui.click(*abs_coords["champ"])
                time.sleep(inputDelay)
                pyautogui.click(*abs_coords["button"])
                break
            else:
                logger.debug(f"Image {image_key} not found, retrying in {sleepTime}s")
            time.sleep(sleepTime)
    except IndexError:
        logger.error(f"Window with title '{window_title}' not found.")
        exit()

def create_log_window(existing_logger):
    """Create a window to display logs and allow log level changes, using an existing logger."""
    def update_log_level(level):
        existing_logger.setLevel(level)
        log_level_label.config(text=f"Current Log Level: {level}")

    def on_change_log_level():
        level = log_level_var.get()
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
        }
        update_log_level(levels.get(level, logging.DEBUG))

    def process_log_queue():
        """Process messages from the queue and update the ScrolledText widget."""
        while not log_queue.empty():
            try:
                log_entry = log_queue.get_nowait()  # Get without blocking
                log_output.insert(tk.END, log_entry + "\n")
                log_output.yview(tk.END)  # Auto-scroll to the end
            except queue.Empty:
                break
        root.after(100, process_log_queue)  # Check the queue again after 100ms

    root = tk.Tk()
    root.title("Log Output")

    # Create a ScrolledText widget to display logs
    log_output = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
    log_output.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Create a queue for log messages
    log_queue = queue.Queue()

    # Redirect logging output to the queue
    class QueueHandler(logging.Handler):
        def __init__(self, log_queue):
            super().__init__()
            self.log_queue = log_queue

        def emit(self, record):
            try:
                log_entry = self.format(record)
                self.log_queue.put(log_entry)
            except Exception:
                self.handleError(record)

    # Attach a QueueHandler to the logger
    queue_handler = QueueHandler(log_queue)
    queue_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    existing_logger.addHandler(queue_handler)
    existing_logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all messages

    # Start processing the log queue
    root.after(100, process_log_queue)

    # Log level selection
    log_level_var = tk.StringVar(value="DEBUG")
    tk.Label(root, text="Log Level:").pack(padx=10, pady=5)
    tk.Radiobutton(root, text="DEBUG", variable=log_level_var, value="DEBUG", command=on_change_log_level).pack(anchor=tk.W)
    tk.Radiobutton(root, text="INFO", variable=log_level_var, value="INFO", command=on_change_log_level).pack(anchor=tk.W)

    log_level_label = tk.Label(root, text="Current Log Level: DEBUG")
    log_level_label.pack(padx=10, pady=5)

    tk.Button(root, text="Close", command=root.destroy).pack(pady=10)

    # Center the window on the screen
    root.update_idletasks()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    root.mainloop()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
#create_log_window(logger)

latest_version = get_latest_version()
champion_names = get_champion_names(latest_version)
logger.info(f"Latest Version: {latest_version} NumChamps: {len(champion_names)}")

champ_image_dir = "images/champs"
files_in_dir = [f for f in os.listdir(champ_image_dir) if os.path.isfile(os.path.join(champ_image_dir, f))]


if len(champion_names) != len(files_in_dir)-1:
    logger.debug(f"More champs in this patch, downloading new champ icons")
    download_champion_images(latest_version, "images/champs")

gui(champion_names)

logger.info(f"pick: {pick} ban: {ban} accept: {accept}")
logger.info(f"pick_choice: {pick_choice} ban_choice: {ban_choice}")

# Activate the target window
#activate_window("League of Legends")

## check there are 


# Look for the "Accept" image if Accept is enabled
if accept:
    logger.info(f"Searching for {images["accept"]}")
    while True:
        if keyboard.is_pressed('esc'):  # Check for escape key
            logger.info(f"Escape key pressed. Exiting...")
            break

        if image_search(images["accept"], "League of Legends"):
            time.sleep(sleepTime)
            pyautogui.click(
                coordinates["accept"][0] + gw.getWindowsWithTitle("League of Legends")[0].left,
                coordinates["accept"][1] + gw.getWindowsWithTitle("League of Legends")[0].top
            )
            break
        else:
           logger.debug(f"Image {"accept"} not found, retrying in {sleepTime}s")
        time.sleep(sleepTime)
else: 
    logger.warning(f"Not accepting, accept option is: {accept}")

# Perform actions for Pick and Ban if enabled and input for pick/ban
if pick and pick_choice != "" and ban_choice != pick_choice:
    search_and_click("pick", pick_choice, "League of Legends")
else:
    logger.warning(f"Not picking, no champ selected, or pick is the same as ban: {ban_choice}")

if ban and ban_choice != "" and ban_choice != pick_choice:
    search_and_click("ban", ban_choice, "League of Legends")
else:
    logger.warning(f"Not banning, no champ selected, or pick is the same as ban: {ban_choice}")

## hotfix for hover champ   
if pick and pick_choice != "" and ban_choice != pick_choice:
    search_and_click("pick", pick_choice, "League of Legends")
else:
    logger.warning(f"Not picking, no champ selected, or pick is the same as ban: {ban_choice}")