import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import tkinter as tk
from tkinter import scrolledtext
import time
import keyboard 
import logging
import queue

# Initialize global variables with default values
pick = True
ban = True
accept = True
pick_choice = ""
ban_choice = ""

sleepTime = 1

# Set the path to images and tolerance
images = {
    "accept": "images/accept.png",
    "pick": "images/pick.png",
    "ban": "images/ban.png"
}
tolerance = 0.8  # Tolerance level for matching

# Coordinates relative to the window
coordinates = {
    "search_bar": (950, 130),
    "champ": (500, 200),
    "button": (800, 750),
    "accept": (800, 750)
}

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


def gui():
    """Create and display a centered GUI window for user input."""
    
    def on_submit():
        global pick, ban, accept, pick_choice, ban_choice
        pick = pick_var.get()
        ban = ban_var.get()
        accept = accept_var.get()
        pick_choice = pick_choice_entry.get()
        ban_choice = ban_choice_entry.get()
        root.destroy()

    root = tk.Tk()
    root.title("Pick/Ban/Accept Selection")

    # Define the input fields and buttons
    tk.Label(root, text="Pick Choice:").grid(row=0, column=0, padx=10, pady=10)
    pick_choice_entry = tk.Entry(root)
    pick_choice_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="Ban Choice:").grid(row=1, column=0, padx=10, pady=10)
    ban_choice_entry = tk.Entry(root)
    ban_choice_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(root, text="Pick").grid(row=2, column=0, padx=10, pady=10)
    pick_var = tk.BooleanVar(value=pick)
    tk.Checkbutton(root, variable=pick_var).grid(row=2, column=1, padx=10, pady=10)

    tk.Label(root, text="Ban").grid(row=3, column=0, padx=10, pady=10)
    ban_var = tk.BooleanVar(value=ban)
    tk.Checkbutton(root, variable=ban_var).grid(row=3, column=1, padx=10, pady=10)

    tk.Label(root, text="Accept").grid(row=4, column=0, padx=10, pady=10)
    accept_var = tk.BooleanVar(value=accept)
    tk.Checkbutton(root, variable=accept_var, state=tk.DISABLED).grid(row=4, column=1, padx=10, pady=10)

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

def perform_action(image_key, input_text, window_title):
    """Search for an image and perform click actions."""
    logger.debug(f"Looking for {image_key} in window '{window_title}'")
    
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        while True:
            if keyboard.is_pressed('esc'):  # Check for escape key
                logger.info("Escape key pressed. Exiting...")
                return

            location = image_search(images[image_key], window_title)
            if location:
                logger.debug(f"Found the image: {image_key}")
                time.sleep(1)

                # Convert relative coordinates to absolute coordinates
                abs_coords = {
                    name: (window.left + x, window.top + y)
                    for name, (x, y) in coordinates.items()
                }

                # Perform actions
                pyautogui.click(*abs_coords["search_bar"])
                time.sleep(1)
                pyautogui.write(input_text, interval=0.1)
                time.sleep(1)
                pyautogui.click(*abs_coords["champ"])
                time.sleep(1)
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

# Execute GUI for user input
gui()

# Activate the target window
#activate_window("League of Legends")

# Look for the "Accept" image if Accept is enabled
if accept:
    while True:
        if keyboard.is_pressed('esc'):  # Check for escape key
            print("Escape key pressed. Exiting...")
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
        time.sleep(1)

# Perform actions for Pick and Ban if enabled
if pick:
    perform_action("pick", pick_choice, "League of Legends")

if ban:
    perform_action("ban", ban_choice, "League of Legends")
