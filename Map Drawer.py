import pygame
import pygame_gui
import json
import sys
import tkinter as tk
from tkinter import filedialog
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1920, 1080
BACKGROUND_COLOR = (255, 255, 255)
CLUSTER_COLOR = (0, 0, 255)
TEXT_COLOR = (0, 0, 0)
GATE_COLOR = (0, 255, 0)  # Green color for the lines representing gates
ZOOM_SCALE = 0.0000001  # Initial zoom scale for the coordinates
HEX_SIZE = 8660000  # Initial size of the hexagons (can be adjusted)

# Set up the screen and the manager for GUI
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cluster Map")
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Scale factor for the coordinates
scale_factor = ZOOM_SCALE

# List to store clusters and gates
clusters = []
gates = []

# Variables to track the movement of the map
dragging_map = False
dragging_cluster = False
last_mouse_pos = (0, 0)
offset_x, offset_y = 0, 0  # To store the offset of the view
selected_cluster = None  # Store the currently selected cluster

# Flag to control whether to show coordinates
show_coordinates = True

# Font for displaying the cluster names and coordinates
font = pygame.font.SysFont('Arial', 20)


def load_json_data_from_file():
    """Open a file dialog and load the selected JSON file."""
    global clusters, gates
    root = tk.Tk()
    root.withdraw()  # Hide the root window (we just need the file dialog)

    # Open file dialog
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])

    if file_path:
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                clusters = data.get('clusters', [])
                gates = data.get('gates', [])
                print("Clusters loaded from file:", clusters)
                print("Gates loaded from file:", gates)
        except Exception as e:
            print(f"Error loading file: {e}")
    else:
        print("No file selected.")


def save_json_data_to_file():
    """Open a file dialog and save the clusters and gates data to a selected file."""
    global clusters, gates
    root = tk.Tk()
    root.withdraw()  # Hide the root window (we just need the file dialog)

    # Open file dialog to choose where to save the file
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])

    if file_path:
        try:
            # Format clusters and gates in the required structure
            data = {
                "clusters": clusters,
                "gates": gates
            }
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
            print("Data saved to file:", file_path)
        except Exception as e:
            print(f"Error saving file: {e}")
    else:
        print("Save operation canceled.")


# Create a button to load JSON from file
load_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH // 2 - 50, HEIGHT - 50), (200, 40)),
                                           text='Load JSON from File',
                                           manager=manager)

# Create a button to save JSON to file
save_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH // 2 - 50, HEIGHT - 100), (200, 40)),
                                           text='Save JSON to File',
                                           manager=manager)

# Create a button to toggle the visibility of coordinates
toggle_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH // 2 - 50, HEIGHT - 150), (200, 40)),
                                             text='Toggle Coordinates',
                                             manager=manager)


def normalize_cluster_name(name):
    """Normalize cluster names (e.g., '001' -> '01', '017' -> '17', skip 'Unknown')."""
    try:
        # Attempt to convert to int and back to string for numeric normalization
        return str(int(name)).zfill(2)
    except (ValueError, TypeError):
        # Return the name as-is for non-numeric strings
        return name


# Function to calculate the points of a hexagon based on its center and size
def get_hexagon_points(center, size):
    """Calculate the points for a hexagon based on its center and size."""
    points = []
    for i in range(6):
        angle = math.pi / 3 * i  # 60 degrees in radians
        x = center[0] + size * math.cos(angle)
        y = center[1] + size * math.sin(angle)
        points.append((x, y))
    return points


# Function to check if a point is inside a hexagon
def is_point_in_hexagon(point, hex_points):
    """Check if a point (mouse position) is inside a hexagon"""
    x, y = point
    inside = False
    n = len(hex_points)
    p1x, p1y = hex_points[0]
    for i in range(n + 1):
        p2x, p2y = hex_points[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def draw_clusters():
    """Draw clusters on the screen as hexagons using scaled coordinates"""
    global selected_cluster

    for cluster in clusters:
        # Scale the coordinates to fit on the screen, applying the offset
        # Flip the X-coordinate horizontally (invert it)
        x = float(cluster['X Coordinate']) * scale_factor + WIDTH // 2 + offset_x
        y = -float(cluster['Z Coordinate']) * scale_factor + HEIGHT // 2 + offset_y

        # Scale the hexagon size based on the zoom level
        hex_size_scaled = HEX_SIZE * scale_factor

        # Get the hexagon points with the new scaled size
        hex_points = get_hexagon_points((x, y), hex_size_scaled)

        # Check if the mouse is inside the hexagon and set it as selected
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if is_point_in_hexagon((mouse_x, mouse_y), hex_points):
            selected_cluster = cluster
        # Draw the hexagon
        pygame.draw.polygon(screen, CLUSTER_COLOR, hex_points)

        # Always display the cluster name
        name_text = f"{cluster['Cluster Name']}"
        name_surface = font.render(name_text, True, TEXT_COLOR)

        # Render the name above the hexagon
        name_pos = (x - name_surface.get_width() // 2, y - hex_size_scaled // 2 - 20)
        screen.blit(name_surface, name_pos)

        # If coordinates are enabled, display them
        if show_coordinates:
            coords_text = f"({cluster['X Coordinate']}, {cluster['Z Coordinate']})"
            coords_surface = font.render(coords_text, True, TEXT_COLOR)

            # Render the coordinates below the hexagon
            coords_pos = (x - coords_surface.get_width() // 2, y + hex_size_scaled // 2 + 5)
            screen.blit(coords_surface, coords_pos)



def draw_gates():
    """Draw lines between clusters for each gate connection."""
    for gate in gates:
        origin_name = gate.get('Origin')
        destination_name = gate.get('Destination')

        # Skip gates with invalid or unknown connections
        if not origin_name or not destination_name or origin_name == "Unknown" or destination_name == "Unknown":
            continue

        # Normalize the cluster names
        origin_name = normalize_cluster_name(origin_name)
        destination_name = normalize_cluster_name(destination_name)

        # Find the origin and destination clusters
        origin_cluster = next((cluster for cluster in clusters if normalize_cluster_name(cluster['Cluster Name']) == origin_name), None)
        destination_cluster = next((cluster for cluster in clusters if normalize_cluster_name(cluster['Cluster Name']) == destination_name), None)

        # If both clusters are found, draw the gate connection
        if origin_cluster and destination_cluster:
            # Get the coordinates for the origin and destination clusters
            origin_x = float(origin_cluster['X Coordinate']) * scale_factor + WIDTH // 2 + offset_x
            origin_y = -float(origin_cluster['Z Coordinate']) * scale_factor + HEIGHT // 2 + offset_y

            dest_x = float(destination_cluster['X Coordinate']) * scale_factor + WIDTH // 2 + offset_x
            dest_y = -float(destination_cluster['Z Coordinate']) * scale_factor + HEIGHT // 2 + offset_y

            # Draw a green line between the clusters (adjusted for flipped coordinates)
            pygame.draw.line(screen, GATE_COLOR, (origin_x, origin_y), (dest_x, dest_y), 2)


def snap_to_grid(value, grid_size):
    """Snap a value to the nearest multiple of grid_size."""
    return round(value / grid_size) * grid_size



# Add a text input field for selecting a cluster
cluster_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((WIDTH // 2 - 100, HEIGHT - 200), (200, 40)),
                                                    manager=manager)

# Track the active cluster being dragged
active_cluster = None
dragging_cluster = False

def find_cluster_by_name(cluster_name):
    """Find a cluster by its name."""
    normalized_name = normalize_cluster_name(cluster_name)
    return next((cluster for cluster in clusters if normalize_cluster_name(cluster['Cluster Name']) == normalized_name), None)

def update_cluster_position(cluster, mouse_pos):
    """Update the position of a cluster based on the current mouse position."""
    # Calculate the new X and Z coordinates based on the mouse position
    x = (mouse_pos[0] - WIDTH // 2 - offset_x) / scale_factor
    z = -(mouse_pos[1] - HEIGHT // 2 - offset_y) / scale_factor

    # Snap the new position to the respective grid sizes for X and Z
    snapped_x = snap_to_grid(x, 15000000)  # Use 15000000 for X
    snapped_z = snap_to_grid(z, 8650000)   # Use 8650000 for Z

    # Check if moving horizontally (left or right)
    if abs(snapped_x - cluster['X Coordinate']) >= 15000000:
        # Determine if the movement is to the left or right
        if snapped_x > cluster['X Coordinate']:  # Moving right
            if int(snapped_x / 15000000) % 2 == 1:  # Odd X position
                snapped_z += 8650000  # Move up in Z
        elif snapped_x < cluster['X Coordinate']:  # Moving left
            if int(snapped_x / 15000000) % 2 == 0:  # Even X position
                snapped_z -= 8650000  # Move down in Z

    # Update the cluster coordinates
    cluster['X Coordinate'] = snapped_x
    cluster['Z Coordinate'] = snapped_z



# Update the main loop to include cluster dragging
def main():
    global scale_factor, offset_x, offset_y, dragging_map, last_mouse_pos, show_coordinates, active_cluster, dragging_cluster

    running = True
    clock = pygame.time.Clock()

    while running:
        screen.fill(BACKGROUND_COLOR)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll Up (Zoom In)
                    scale_factor *= 1.1
                elif event.button == 5:  # Scroll Down (Zoom Out)
                    scale_factor *= 0.9
                elif event.button == 2:  # Middle Mouse Button (Start dragging the map)
                    dragging_map = True
                    last_mouse_pos = event.pos
                elif event.button == 1 and active_cluster:  # Left Mouse Button for moving selected cluster
                    dragging_cluster = True
                elif event.button == 3 and active_cluster:  # Right Mouse Button to release the cluster
                    dragging_cluster = False
                    active_cluster = None  # Deselect the cluster

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:
                    dragging_map = False

            elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                if event.ui_element == cluster_input:
                    cluster_name = event.text
                    active_cluster = find_cluster_by_name(cluster_name)
                    if active_cluster:
                        print(f"Cluster {cluster_name} selected for movement.")
                    else:
                        print(f"No cluster found with name {cluster_name}.")

            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == load_button:
                    load_json_data_from_file()
                elif event.ui_element == save_button:
                    save_json_data_to_file()
                elif event.ui_element == toggle_button:
                    show_coordinates = not show_coordinates

            manager.process_events(event)

        # Move the map when dragging
        if dragging_map:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            delta_x = mouse_x - last_mouse_pos[0]
            delta_y = mouse_y - last_mouse_pos[1]
            offset_x += delta_x
            offset_y += delta_y
            last_mouse_pos = (mouse_x, mouse_y)

        # Move the active cluster when dragging
        if dragging_cluster and active_cluster:
            mouse_pos = pygame.mouse.get_pos()
            update_cluster_position(active_cluster, mouse_pos)

        # Draw gates and clusters
        draw_gates()
        draw_clusters()

        # Update the GUI
        manager.update(clock.tick(60) / 1000.0)

        # Render the display
        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()




if __name__ == "__main__":
    main()