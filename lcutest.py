from lcu_driver import Connector
import asyncio
import requests
import logging
import tkinter as tk
from tkinter import ttk

# Initialize global variables with default values
pick = True
ban = True
accept = False
pick_choice = ""
ban_choice = ""

# Initialize Logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

connector = Connector()

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
        return [champ['name'] for champ in champions.values()]
    else:
        return []

async def submit_pick_ban(connection):
    """Submit champion pick and ban using the LCU API."""
    if pick_choice:
        logger.info(f"Attempting to pick champion: {pick_choice}")
        await connection.request('patch', '/lol-champ-select/v1/session/actions/1', data={"championId": get_champion_id(pick_choice), "completed": True})

    if ban_choice:
        logger.info(f"Attempting to ban champion: {ban_choice}")
        await connection.request('patch', '/lol-champ-select/v1/session/actions/2', data={"championId": get_champion_id(ban_choice), "completed": True})

def get_champion_id(champion_name):
    """Get champion ID from champion name."""
    version = get_latest_version()
    champion_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
    response = requests.get(champion_url)
    champion_data = response.json()['data']
    
    for champ in champion_data.values():
        if champ['name'].lower() == champion_name.lower():
            return int(champ['key'])
    logger.error(f"Champion {champion_name} not found.")
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

@connector.ready
async def connect(connection):
    logger.info("Connected to the League Client API")
    await asyncio.sleep(1)  # Allow time for session to initialize
    
    latest_version = get_latest_version()
    champion_names = get_champion_names(latest_version)

    # gui(champion_names)

    # if pick or ban:
    #     await submit_pick_ban(connection)

@connector.close
async def disconnect(_):
    logger.info("Disconnected from the League Client API")

# Start the connector
connector.start()
