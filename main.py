import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yaml

# Function to save the settings instantly upon change
def update_settings():
    settings = {
        'enabled': enabled_var.get(),
        'run': {
            'disable_mc': disable_mc_var.get(),
            'disable_downloads': disable_downloads_var.get(),
            'disable_phone': disable_phone_var.get(),
            'disable_websites': disable_websites_var.get(),
        },
        'settings': {
            'kill_java_interval': int(kill_java_interval_var.get()),
            'disable_downloads_interval': int(disable_downloads_interval_var.get()),
            'disable_websites_interval': int(disable_websites_interval_var.get()),
            'firefox_profile_path': firefox_profile_path_var.get(),
        }
    }
    file_path = "settings.yml"
    with open(file_path, 'w') as file:
        yaml.dump(settings, file)

# Animation for slide switch
def animate_toggle(btn, var):
    current_color = btn.cget("bg")
    target_color = "#43B581" if var.get() else "#72767d"
    step = 1

    def color_fade():
        nonlocal step
        if step <= 20:
            r1, g1, b1 = int(current_color[1:3], 16), int(current_color[3:5], 16), int(current_color[5:7], 16)
            r2, g2, b2 = int(target_color[1:3], 16), int(target_color[3:5], 16), int(target_color[5:7], 16)

            new_color = "#%02x%02x%02x" % (
                int(r1 + (r2 - r1) * step / 20),
                int(g1 + (g2 - g1) * step / 20),
                int(b1 + (b2 - b1) * step / 20)
            )
            btn.config(bg=new_color)
            step += 1
            root.after(10, color_fade)

    color_fade()

# Function to toggle the switch
def toggle_switch(btn, var):
    var.set(not var.get())
    animate_toggle(btn, var)
    update_settings()

# Create the main window
root = tk.Tk()
root.title("Settings Editor - Dark Mode")
root.geometry("400x400")
root.configure(bg="#2c2f33")

# Variables for settings
enabled_var = tk.BooleanVar(value=True)
disable_mc_var = tk.BooleanVar(value=False)
disable_downloads_var = tk.BooleanVar(value=False)
disable_phone_var = tk.BooleanVar(value=False)
disable_websites_var = tk.BooleanVar(value=False)
kill_java_interval_var = tk.StringVar(value="10")
disable_downloads_interval_var = tk.StringVar(value="3")
disable_websites_interval_var = tk.StringVar(value="10")
firefox_profile_path_var = tk.StringVar(value="/home/sand/snap/firefox/common/.mozilla/firefox/zvfmrorl.default")

# Create dark mode style elements
def create_label(text, row, column):
    label = tk.Label(root, text=text, fg="white", bg="#2c2f33")
    label.grid(row=row, column=column, padx=10, pady=5, sticky="w")

# Function to create entry fields and bind Enter key to update settings
def create_entry(var, row, column):
    entry = tk.Entry(root, textvariable=var, bg="#23272a", fg="white", insertbackground="white")
    entry.grid(row=row, column=column, padx=10, pady=5)
    
    # Bind Enter key to trigger the update_settings function
    entry.bind('<Return>', lambda event: update_settings())

def create_switch(row, column, var):
    switch_btn = tk.Canvas(root, width=40, height=20, bg="#72767d", bd=0, highlightthickness=0)
    switch_btn.grid(row=row, column=column, padx=10, pady=5, sticky="w")

    def on_click(event):
        toggle_switch(switch_btn, var)

    switch_btn.bind("<Button-1>", on_click)
    update_switch(switch_btn, var)

def update_switch(btn, var):
    if var.get():
        btn.config(bg="#43B581")
    else:
        btn.config(bg="#72767d")

# Enabled setting
create_label("Enabled:", 0, 0)
enabled_check = tk.Checkbutton(root, variable=enabled_var, bg="#2c2f33", fg="white", selectcolor="#23272a", command=update_settings)
enabled_check.grid(row=0, column=1, sticky="w")

# Run settings with switches
create_label("Disable MC:", 1, 0)
create_switch(1, 1, disable_mc_var)

create_label("Disable Downloads:", 2, 0)
create_switch(2, 1, disable_downloads_var)

create_label("Disable Phone:", 3, 0)
create_switch(3, 1, disable_phone_var)

create_label("Disable Websites:", 4, 0)
create_switch(4, 1, disable_websites_var)

# Settings intervals
create_label("Kill Java Interval:", 5, 0)
create_entry(kill_java_interval_var, 5, 1)

create_label("Disable Downloads Interval:", 6, 0)
create_entry(disable_downloads_interval_var, 6, 1)

create_label("Disable Websites Interval:", 7, 0)
create_entry(disable_websites_interval_var, 7, 1)

create_label("Firefox Profile Path:", 8, 0)
create_entry(firefox_profile_path_var, 8, 1)

# Run the application
root.mainloop()
