import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk  # Import Resampling conditionally
import pyperclip  # For copying text to clipboard

# Attempt to import Resampling; fallback if not available
try:
    from PIL import Resampling
    resample_filter = Resampling.LANCZOS
except ImportError:
    resample_filter = Image.LANCZOS  # For Pillow versions <10.0.0

# Initialize the Tkinter main window
root = tk.Tk()
root.title("Easy Grid Locations for Cosmoteer")
root.geometry('600x200')  # Set initial window size

# Create labels and entry fields for X and Y size inputs
label_x = tk.Label(root, text="X Size:", font=("Consolas", 12))
label_x.grid(row=0, column=0, padx=20, pady=10, sticky="e")
entry_x = tk.Entry(root, font=("Consolas", 12))
entry_x.grid(row=0, column=1, padx=20, pady=10, sticky="w")

label_y = tk.Label(root, text="Y Size:", font=("Consolas", 12))
label_y.grid(row=1, column=0, padx=20, pady=10, sticky="e")
entry_y = tk.Entry(root, font=("Consolas", 12))
entry_y.grid(row=1, column=1, padx=20, pady=10, sticky="w")

# Button to submit the size and create the grid
def submit_size():
    try:
        x_size = int(entry_x.get())
        y_size = int(entry_y.get())
        if x_size <= 0 or y_size <= 0:
            raise ValueError
        create_grid(x_size, y_size)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid positive integers for X and Y size.")

submit_button = tk.Button(root, text="Submit Size", command=submit_size, font=("Consolas", 12), bg="lightblue")
submit_button.grid(row=2, column=0, columnspan=2, padx=20, pady=10)

# Create a grid with perimeter for door locations and show a key
def create_grid(x_size, y_size):
    # Create a new window for the grid editor
    grid_window = tk.Toplevel(root)
    grid_window.title(f"Grid Editor for {x_size}x{y_size} Part")

    # Define cell size
    cell_size = 40  # Size per cell in pixels

    # Calculate window size
    grid_width = cell_size * (x_size + 2)
    grid_height = cell_size * (y_size + 2)
    window_width = max(grid_width + 100, 800)  # Ensure minimum width of 800
    window_height = grid_height + 300  # Extra space for instructions and color key

    # Set minimum window size to ensure UI elements are visible
    grid_window.minsize(window_width, window_height)

    # Set initial window size
    grid_window.geometry(f"{window_width}x{window_height}")

    # Main frame to hold all elements
    main_frame = tk.Frame(grid_window)
    main_frame.grid(row=0, column=0, sticky="nsew")
    grid_window.columnconfigure(0, weight=1)
    grid_window.rowconfigure(0, weight=1)

    # Instructions
    instruction_label = tk.Label(
        main_frame,
        text="Click cells to toggle block status or door locations.\n"
             "Gray = Blocked, Green = Allowed Door, Red = Disabled Door",
        font=("Consolas", 12),
        justify="center"
    )
    instruction_label.grid(row=0, column=0, padx=10, pady=10, sticky="n")

    # Buttons frame
    buttons_frame = tk.Frame(main_frame)
    buttons_frame.grid(row=1, column=0, pady=(0, 10))

    # Function to upload and overlay image
    def upload_image():
        nonlocal image, image_tk
        file_path = filedialog.askopenfilename(
            filetypes=[("PNG Images", "*.png"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                # Open and resize image to fit the internal grid (excluding perimeter)
                img = Image.open(file_path).convert("RGBA")
                internal_width = cell_size * x_size
                internal_height = cell_size * y_size
                img = img.resize((internal_width, internal_height), resample_filter)

                # Apply transparency to the image
                alpha = 150  # Adjust transparency level (0-255)
                img.putalpha(alpha)

                image = img
                image_tk = ImageTk.PhotoImage(img)

                # Display the image on the canvas
                # Remove previous image if any
                canvas.delete("uploaded_image")
                # Calculate position to place the image (offset by cell_size)
                image_id = canvas.create_image(cell_size, cell_size, anchor="nw", image=image_tk, tags="uploaded_image")
                # Lower the image below the grid lines but above the background
                canvas.tag_lower("uploaded_image", "grid_lines")
            except Exception as e:
                messagebox.showerror("Image Error", f"Failed to load image:\n{e}")

    # Button to upload image
    upload_button = tk.Button(buttons_frame, text="Upload Image", command=upload_image, font=("Consolas", 12), bg="lightgreen")
    upload_button.pack(side="left", padx=10)

    # Function to generate the output code
    def generate_code():
        # Initialize empty lists for the arrays
        blocked_cells = []
        door_locations = []
        phys_rect = f"size = [{x_size}, {y_size}]"

        # Helper function to identify corner cells
        def is_corner_inner(x, y):
            return (x == 0 and y == 0) or \
                   (x == 0 and y == y_size + 1) or \
                   (x == x_size + 1 and y == 0) or \
                   (x == x_size + 1 and y == y_size + 1)

        # Process the blocked travel cells
        for y in range(1, y_size + 1):
            for x in range(1, x_size + 1):
                state = cell_states[y][x]
                if state == 'blocked':
                    blocked_cells.append(f"\t\t[{x - 1}, {y - 1}]")
                else:
                    blocked_cells.append(f"\t\t/* [{x - 1}, {y - 1}] */")  # Commented out by default

        # Process door locations for all perimeter cells, excluding corners
        for x in range(x_size + 2):
            # Top edge (y=0), exclude corners
            if not is_corner_inner(x, 0):
                state = cell_states[0][x]
                if state == 'allowed_door':
                    door_locations.append(f"\t\t[{x - 1}, -1]")
                elif state == 'disabled_door':
                    door_locations.append(f"\t\t/* Disabled Door at [{x - 1}, -1] */")

            # Bottom edge (y=y_size+1), exclude corners
            if not is_corner_inner(x, y_size + 1):
                state = cell_states[y_size + 1][x]
                if state == 'allowed_door':
                    door_locations.append(f"\t\t[{x - 1}, {y_size}]")
                elif state == 'disabled_door':
                    door_locations.append(f"\t\t/* Disabled Door at [{x - 1}, {y_size}] */")

        for y in range(1, y_size + 1):
            # Left edge (x=0), exclude corners
            if not is_corner_inner(0, y):
                state = cell_states[y][0]
                if state == 'allowed_door':
                    door_locations.append(f"\t\t[-1, {y - 1}]")
                elif state == 'disabled_door':
                    door_locations.append(f"\t\t/* Disabled Door at [-1, {y - 1}] */")

            # Right edge (x=x_size+1), exclude corners
            if not is_corner_inner(x_size + 1, y):
                state = cell_states[y][x_size + 1]
                if state == 'allowed_door':
                    door_locations.append(f"\t\t[{x_size}, {y - 1}]")
                elif state == 'disabled_door':
                    door_locations.append(f"\t\t/* Disabled Door at [{x_size}, {y - 1}] */")

        # Format output for BlockedTravelCells and AllowedDoorLocations
        output_code = (
            "AllowedDoorLocations\n[\n" + "\n".join(door_locations) + "\n]\n\n"
            "BlockedTravelCells\n[\n" + "\n".join(blocked_cells) + "\n]\n\n"
            f"size = [{x_size}, {y_size}]\n\n"
            "PhysRects\n[\n\t\tsize = [" + f"{x_size}, {y_size}" + "]\n]\n"
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

    # Button to generate code
    generate_button = tk.Button(buttons_frame, text="Generate Code", command=generate_code, font=("Consolas", 12))
    generate_button.pack(side="left", padx=10)

    # Canvas frame
    canvas_frame = tk.Frame(main_frame)
    canvas_frame.grid(row=2, column=0, pady=10)

    canvas = tk.Canvas(canvas_frame, width=grid_width, height=grid_height)
    canvas.pack()

    # Load image variables
    image = None
    image_tk = None

    # Create a list to hold the cell states
    # Each cell will have a state: 'unblocked', 'blocked', 'allowed_door', 'disabled_door'
    cell_states = [[None for _ in range(x_size + 2)] for _ in range(y_size + 2)]

    # Helper function to identify corner cells
    def is_corner(x, y):
        return (x == 0 and y == 0) or \
               (x == 0 and y == y_size + 1) or \
               (x == x_size + 1 and y == 0) or \
               (x == x_size + 1 and y == y_size + 1)

    # Draw grid lines
    for y in range(y_size + 3):
        canvas.create_line(0, y * cell_size, grid_width, y * cell_size, fill="black", tags="grid_lines")
    for x in range(x_size + 3):
        canvas.create_line(x * cell_size, 0, x * cell_size, grid_height, fill="black", tags="grid_lines")

    # Initialize the grid
    for y in range(y_size + 2):
        for x in range(x_size + 2):
            x1 = x * cell_size
            y1 = y * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size

            display_x = x - 1  # Adjust label for correct coordinate system
            display_y = y - 1

            if is_corner(x, y):
                # Corner cells: display as disabled rectangles
                # No fill to keep transparent
                rect = canvas.create_rectangle(x1, y1, x2, y2, outline="", tags=f"cell_{x}_{y}")
                # Draw the text label
                canvas.create_text(x1 + cell_size/2, y1 + cell_size/2, text=f"[{display_x},{display_y}]", font=("Consolas", 10))
                cell_states[y][x] = 'corner'
            elif x == 0 or x == x_size + 1 or y == 0 or y == y_size + 1:
                # Edge cells (door locations)
                rect = canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="", tags=f"door_{x}_{y}")
                # Initial color for allowed doors
                color = "green"
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="", tags=f"door_fill_{x}_{y}")
                # Draw the text label
                canvas.create_text(x1 + cell_size/2, y1 + cell_size/2, text=f"[{display_x},{display_y}]", font=("Consolas", 10))
                cell_states[y][x] = 'allowed_door'
            else:
                # Internal cells (unblocked by default)
                rect = canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="", tags=f"cell_{x}_{y}")
                # Draw the text label
                canvas.create_text(x1 + cell_size/2, y1 + cell_size/2, text=f"[{display_x},{display_y}]", font=("Consolas", 10))
                cell_states[y][x] = 'unblocked'

    # Function to toggle cell state based on click
    def on_canvas_click(event):
        # Determine which cell was clicked
        x_click = event.x // cell_size
        y_click = event.y // cell_size

        if y_click < 0 or y_click > y_size + 1 or x_click < 0 or x_click > x_size + 1:
            return  # Click outside grid

        current_state = cell_states[y_click][x_click]

        if current_state == 'corner':
            return  # Do nothing for corner cells
        elif current_state in ['allowed_door', 'disabled_door']:
            # Toggle door state
            tag = f"door_fill_{x_click}_{y_click}"
            if current_state == 'allowed_door':
                # Change to disabled door
                cell_states[y_click][x_click] = 'disabled_door'
                color = "red"
            else:
                # Change to allowed door
                cell_states[y_click][x_click] = 'allowed_door'
                color = "green"
            # Update rectangle color
            canvas.itemconfig(tag, fill=color)
        elif current_state in ['unblocked', 'blocked']:
            # Toggle block state
            tag = f"cell_fill_{x_click}_{y_click}"
            if current_state == 'unblocked':
                # Change to blocked
                cell_states[y_click][x_click] = 'blocked'
                color = "gray"
                canvas.create_rectangle(x_click * cell_size, y_click * cell_size,
                                        (x_click + 1) * cell_size, (y_click + 1) * cell_size,
                                        fill=color, outline="", tags=tag)
            else:
                # Change to unblocked
                cell_states[y_click][x_click] = 'unblocked'
                canvas.delete(tag)

    # Bind click event to the canvas
    canvas.bind("<Button-1>", on_canvas_click)

    # Color Key
    key_frame = tk.Frame(main_frame)
    key_frame.grid(row=3, column=0, pady=10)

    tk.Label(key_frame, text="Color Key:", font=("Consolas", 10, "bold")).pack(pady=5)
    tk.Label(key_frame, text=" No Fill = Unblocked ", font=("Consolas", 10), relief="solid", width=20).pack(padx=5, pady=2)
    tk.Label(key_frame, text=" Gray = Blocked ", bg="gray", font=("Consolas", 10), relief="solid", width=20).pack(padx=5, pady=2)
    tk.Label(key_frame, text=" Green = Allowed Door ", bg="green", font=("Consolas", 10), relief="solid", width=20).pack(padx=5, pady=2)
    tk.Label(key_frame, text=" Red = Disabled Door ", bg="red", font=("Consolas", 10), relief="solid", width=20).pack(padx=5, pady=2)

    # Configure grid weights for resizing
    grid_window.rowconfigure(0, weight=1)
    main_frame.rowconfigure(2, weight=1)

# Run the Tkinter main loop
root.mainloop()
