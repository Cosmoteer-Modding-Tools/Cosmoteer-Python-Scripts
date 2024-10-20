import tkinter as tk
from tkinter import messagebox
import pyperclip  # For copying text to clipboard

# Initialize the Tkinter window with larger size and centered layout
root = tk.Tk()
root.title("Easy Grid Locations for Cosmoteer")
root.geometry('400x200')  # Set a bigger window size

# Create labels and entry fields for X and Y size inputs
label_x = tk.Label(root, text="X Size:", font=("Consolas", 12))
label_x.grid(row=0, column=0, padx=20, pady=10, sticky="w")
entry_x = tk.Entry(root, font=("Consolas", 12))
entry_x.grid(row=0, column=1, padx=20, pady=10)

label_y = tk.Label(root, text="Y Size:", font=("Consolas", 12))
label_y.grid(row=1, column=0, padx=20, pady=10, sticky="w")
entry_y = tk.Entry(root, font=("Consolas", 12))
entry_y.grid(row=1, column=1, padx=20, pady=10)

# Button to submit the size and create the grid
def submit_size():
    try:
        x_size = int(entry_x.get())
        y_size = int(entry_y.get())
        create_grid(x_size, y_size)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid integers for X and Y size.")

submit_button = tk.Button(root, text="Submit Size", command=submit_size, font=("Consolas", 12), bg="lightblue")
submit_button.grid(row=2, column=0, columnspan=2, padx=20, pady=10)

# Create a grid with perimeter for door locations and show a key
def create_grid(x_size, y_size):
    # Create a new window for the grid
    grid_window = tk.Toplevel(root)
    grid_window.title(f"Grid Editor for {x_size}x{y_size} Part")

    # Set a minimum window size to ensure instructions, buttons, and key are visible
    min_width = 1000
    min_height = 1000  # User's preferred size
    button_size = 90  # Size per button (in pixels)
    padding = 180  # Additional padding for buttons, instructions, and color key
    window_width = max(button_size * (x_size + 2), min_width)  # Adjust width for grid and doors
    window_height = max(button_size * (y_size + 3) + padding, min_height)  # Adjust height for UI
    grid_window.geometry(f"{window_width}x{window_height}")  # Set window size dynamically

    # Main frame to hold all elements
    main_frame = tk.Frame(grid_window)
    main_frame.pack(fill="both", expand=True)

    # Instructions
    instruction_label = tk.Label(main_frame, text="Click cells to toggle block status or door locations.\nGray = Blocked, Green = Allowed Door, Red = Disabled Door", font=("Consolas", 12), pady=10)
    instruction_label.pack()

    # Grid frame for placing buttons
    grid_frame = tk.Frame(main_frame)
    grid_frame.pack()

    # Create a list to hold the button states for blocked cells and doors
    grid_buttons = [[None for _ in range(x_size + 2)] for _ in range(y_size + 2)]

    # Create the buttons for each grid cell (make buttons square with consistent size)
    for y in range(y_size + 2):
        for x in range(x_size + 2):
            if x == 0 or x == x_size + 1 or y == 0 or y == y_size + 1:
                # Edge cells (door locations)
                display_x = x - 1  # Adjust label for correct coordinate system
                display_y = y - 1
                btn_door = tk.Button(grid_frame, text=f"[{display_x},{display_y}]", bg="green", width=6, height=3,
                                     font=("Consolas", 10),
                                     command=lambda x=x, y=y: toggle_door(x, y, grid_buttons))
                btn_door.grid(row=y, column=x)  # Place button in grid layout
                grid_buttons[y][x] = btn_door
            else:
                # Internal cells (blocked or unblocked)
                btn_block = tk.Button(grid_frame, text=f"[{x-1},{y-1}]", bg="white", width=6, height=3,
                                      font=("Consolas", 10),
                                      command=lambda x=x, y=y: toggle_block(x, y, grid_buttons))
                btn_block.grid(row=y, column=x)  # Place button in grid layout
                grid_buttons[y][x] = btn_block

    # Frame for Generate Code button
    button_frame = tk.Frame(main_frame)
    button_frame.pack(pady=20)

    # Button to generate the final code after grid interaction
    generate_button = tk.Button(button_frame, text="Generate Code", font=("Consolas", 12), command=lambda: generate_code(x_size, y_size, grid_buttons))
    generate_button.pack()

    # Frame for the color key at the bottom
    key_frame = tk.Frame(main_frame)
    key_frame.pack(pady=10)

    # Add a color key using colored text
    tk.Label(key_frame, text="Color Key:", font=("Consolas", 10)).grid(row=0, column=0, padx=10)
    tk.Label(key_frame, text=" White = Unblocked ", bg="white", font=("Consolas", 10), relief="solid", width=20).grid(row=0, column=1, padx=10)
    tk.Label(key_frame, text=" Gray = Blocked ", bg="gray", font=("Consolas", 10), relief="solid", width=20).grid(row=0, column=2, padx=10)
    tk.Label(key_frame, text=" Green = Allowed Door ", bg="green", font=("Consolas", 10), relief="solid", width=20).grid(row=0, column=3, padx=10)
    tk.Label(key_frame, text=" Red = Disabled Door ", bg="red", font=("Consolas", 10), relief="solid", width=20).grid(row=0, column=4, padx=10)

# Toggle block state (internal cells)
def toggle_block(x, y, grid_buttons):
    btn = grid_buttons[y][x]
    if btn.cget("bg") == "white":
        btn.config(bg="gray")  # Blocked travel cell
    else:
        btn.config(bg="white")  # Unblocked travel cell

# Toggle door state (perimeter cells)
def toggle_door(x, y, grid_buttons):
    btn = grid_buttons[y][x]
    if btn.cget("bg") == "green":
        btn.config(bg="red")  # Disabled door location
    else:
        btn.config(bg="green")  # Enabled door location

# Generate the output code based on user interaction and display in a text box
def generate_code(x_size, y_size, grid_buttons):
    # Initialize empty lists for the arrays
    blocked_cells = []
    door_locations = []
    phys_rect = f"size = [{x_size}, {y_size}]"

    # Process the blocked travel cells
    for y in range(1, y_size + 1):
        for x in range(1, x_size + 1):
            if grid_buttons[y][x].cget("bg") == "gray":
                blocked_cells.append("\t\t[{}, {}]".format(x - 1, y - 1))
            else:
                blocked_cells.append("\t\t/* [{}, {}] */".format(x - 1, y - 1))  # Commented out by default

    # Process door locations for all perimeter cells
    for x in range(x_size + 2):
        if grid_buttons[0][x].cget("bg") == "green":
            door_locations.append("\t\t[{}, -1]".format(x - 1))  # Top edge
        if grid_buttons[y_size + 1][x].cget("bg") == "green":
            door_locations.append("\t\t[{}, {}]".format(x - 1, y_size))  # Bottom edge

    for y in range(1, y_size + 1):
        if grid_buttons[y][0].cget("bg") == "green":
            door_locations.append("\t\t[-1, {}]".format(y - 1))  # Left edge
        if grid_buttons[y][x_size + 1].cget("bg") == "green":
            door_locations.append("\t\t[{}, {}]".format(x_size, y - 1))  # Right edge

    # Format output for BlockedTravelCells and AllowedDoorLocations
    output_code = (
        "\tAllowedDoorLocations\n\t[\n" + "\n".join(door_locations) + "\n\t]\n\n"
        "\tBlockedTravelCells\n\t[\n" + "\n".join(blocked_cells) + "\n\t]\n\n"
        f"\tsize = [{x_size}, {y_size}]\n\n"
        f"\tPhysRects\n\t[\n\t\tsize = [{x_size}, {y_size}]\n\t]\n"
    )

    # Display the output code in a text window
    code_window = tk.Toplevel(root)
    code_window.title("Generated Code")
    code_window.geometry(f"600x500")  # Set window size large enough to avoid scroll

    text_box = tk.Text(code_window, wrap="word", font=("Consolas", 10), bg="lightyellow")
    text_box.insert("1.0", output_code)
    text_box.pack(expand=True, fill="both")

    # Button to copy the code to the clipboard
    def copy_to_clipboard():
        pyperclip.copy(text_box.get("1.0", "end-1c"))
        messagebox.showinfo("Copied", "Code copied to clipboard!")

    # Button placed below the text box
    copy_button = tk.Button(code_window, text="Copy to Clipboard", font=("Consolas", 12), command=copy_to_clipboard)
    copy_button.pack(pady=10)

# Run the Tkinter main loop
root.mainloop()
