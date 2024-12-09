import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import xml.etree.ElementTree as ET
import os
import re
import json


# Create the main tkinter window
root = tk.Tk()
root.title("Cluster and Gate Viewer")


def normalize_cluster_name(name):
    """
    Normalizes a cluster or gate identifier to match the expected format:
    - Handles case-insensitive patterns (e.g., ClusterGateXXX or clustergateXXX → HBX).
    - Cluster_XXX → X for original clusters.
    """
    # Normalize original clusters (e.g., Cluster_009_connection → 9)
    match = re.search(r"Cluster_(\d+)_connection", name, re.IGNORECASE)
    if match:
        return str(int(match.group(1)))  # Remove leading zeros

    # Normalize homebrew clusters (e.g., homebrew_connection_ClusterGate009 → HB9)
    match = re.search(r"(Cluster|clustergate)(\d+)", name, re.IGNORECASE)
    if match:
        return f"HB{int(match.group(2))}"  # Add HB and remove leading zeros

    return name  # Return name unchanged if no match



# Function to load multiple XML files
def load_files():
    filenames = filedialog.askopenfilenames(filetypes=[("XML Files", "*.xml")])
    if filenames:
        all_clusters = []
        all_gates = []

        for filename in filenames:
            all_clusters.extend(extract_cluster_info(filename))
            all_gates.extend(extract_gate_info(filename))

        # Debug: Print out the gates data
        print("Loaded gates data:", all_gates)

        display_clusters(all_clusters)
        display_gates(all_gates)

        # Store the clusters to use when creating the map
        global current_clusters
        current_clusters = all_clusters

# Treeview for clusters
tree_clusters = ttk.Treeview(root, columns=("Connection Name", "Cluster Name", "X Coordinate", "Y Coordinate", "Z Coordinate", "Connection Type"), show="headings")
tree_clusters.heading("Connection Name", text="Connection Name")
tree_clusters.heading("Cluster Name", text="Cluster Name")  # Add heading for Cluster Name
tree_clusters.heading("X Coordinate", text="X Coordinate")
tree_clusters.heading("Y Coordinate", text="Y Coordinate")
tree_clusters.heading("Z Coordinate", text="Z Coordinate")
tree_clusters.heading("Connection Type", text="Connection Type")
tree_clusters.pack(pady=10)




# Function to save clusters and gates to a JSON file
def save_to_json():
    if not current_clusters:
        messagebox.showinfo("Info", "No cluster data to save!")
        return

    # Extract clusters and gates data
    clusters_data = current_clusters
    gates_data = []
    for row in tree_gates.get_children():
        gate_values = tree_gates.item(row, "values")
        gates_data.append({
            "Gate Name": gate_values[0],
            "Origin": gate_values[1],
            "Destination": gate_values[2]
        })

    # Combine data into a dictionary
    data_to_save = {
        "clusters": clusters_data,
        "gates": gates_data
    }

    # Prompt the user to select a location and name for the JSON file
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json")],
        title="Save As"
    )
    if not file_path:
        return  # If the user cancels, do nothing

    try:
        # Write the data to the selected file
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(data_to_save, json_file, indent=4)
        messagebox.showinfo("Success", f"Data saved to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while saving the file: {e}")


# Add a button to save to JSON in the main GUI
save_json_button = tk.Button(root, text="Save to JSON", command=save_to_json)
save_json_button.pack(pady=10)

def extract_sector_number(connection_name):
    match = re.search(r'(\d+)', connection_name)  # Match the number after "Cluster_" or "homebrew_cluster"
    if match:
        return int(match.group(1))  # Return the first number as an integer
    return None  # If no match found

# Function to extract cluster data
def extract_cluster_info(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    clusters = []
    for connection in root.findall(".//connection"):
        connection_name = connection.get('name')
        position = connection.find('offset/position')
        connection_type = ""

        macro = connection.find('macro')
        if macro is not None:
            connection_type = macro.get('connection', "")

        if connection_name and position is not None:
            x = convert_to_real_number(position.get('x'))
            y = position.get('y')  # Y is not used for overlaps but included for completeness
            z = convert_to_real_number(position.get('z'))

            # Normalize cluster names
            cluster_name = normalize_cluster_name(connection_name)

            clusters.append({
                'Connection Name': connection_name,
                'Cluster Name': cluster_name,  # Use normalized cluster name
                'X Coordinate': x,
                'Y Coordinate': y,
                'Z Coordinate': z,
                'Connection Type': connection_type
            })
    return clusters





# Function to extract gate data
def extract_gate_info(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    gates = []
    for connection in root.findall(".//connection[@ref='destination']"):
        path = connection.get('path', "")
        gate_name = os.path.basename(path)  # Extract the last part of the path

        # Patterns for gate connections (case-insensitive)
        homebrew_to_original = re.search(r"homebrew_connection_(Cluster|clustergate)(\d+)to(\d+)", gate_name, re.IGNORECASE)
        original_to_homebrew = re.search(r"connection_homebrew_(Cluster|clustergate)(\d+)To(\d+)", gate_name, re.IGNORECASE)
        original_to_original = re.search(r"(Cluster|clustergate)(\d{3})To(\d{3})", gate_name, re.IGNORECASE)

        if homebrew_to_original:
            # Normalize: Origin as Homebrew, Destination as Original
            origin = f"HB{int(homebrew_to_original.group(2))}"  # Remove leading zeros
            destination = str(int(homebrew_to_original.group(3)))  # Normalize original
        elif original_to_homebrew:
            # Normalize: Origin as Original, Destination as Homebrew
            origin = str(int(original_to_homebrew.group(2)))  # Normalize original
            destination = f"HB{int(original_to_homebrew.group(3))}"  # Normalize homebrew
        elif original_to_original:
            # Normalize both Origin and Destination as Original
            origin = normalize_cluster_name(f"Cluster_{int(original_to_original.group(2))}_connection")  # Normalize original
            destination = normalize_cluster_name(f"Cluster_{int(original_to_original.group(3))}_connection")
        else:
            origin, destination = "Unknown", "Unknown"

        gates.append({
            'Gate Name': gate_name,
            'Origin': origin,
            'Destination': destination
        })

    return gates







# Create a button to load the XML files
load_button = tk.Button(root, text="Load XML Files", command=load_files)
load_button.pack(pady=10)


# Function to display clusters in the first Treeview
def display_clusters(clusters):
    for row in tree_clusters.get_children():
        tree_clusters.delete(row)

    for cluster in clusters:
        tree_clusters.insert("", "end", values=(
            cluster['Connection Name'],
            cluster['Cluster Name'],  # Display the cluster name
            cluster['X Coordinate'],
            cluster['Y Coordinate'],
            cluster['Z Coordinate'],
            cluster['Connection Type']
        ))



# Function to handle double-click and enable cell editing
def edit_cluster(event):
    # Get the selected item
    selected_item = tree_clusters.selection()
    if not selected_item:
        return

    # Get the row and column where the double-click occurred
    region = tree_clusters.identify_region(event.x, event.y)
    if region != "cell":
        return

    column = tree_clusters.identify_column(event.x)
    row_id = tree_clusters.identify_row(event.y)
    column_index = int(column[1:]) - 1  # Convert column name (#1, #2...) to index

    # Map column names to editable indices dynamically
    column_name_to_index = {
        "X Coordinate": 2,
        "Y Coordinate": 3,
        "Z Coordinate": 4,
    }
    column_name = tree_clusters.heading(column)["text"]  # Get column header text
    if column_name not in column_name_to_index:
        return  # Skip if column is not editable

    # Allow editing only for coordinate columns
    editable_index = column_name_to_index[column_name]

    # Get the current value
    current_value = tree_clusters.item(row_id, "values")[editable_index]

    # Create an Entry widget and place it over the selected cell
    x, y, width, height = tree_clusters.bbox(row_id, column)
    entry = tk.Entry(tree_clusters, width=10)
    entry.place(x=x, y=y, width=width, height=height)
    entry.insert(0, current_value)  # Pre-fill the entry with the current value

    # Function to save the edited value
    def save_edit(event=None):
        new_value = entry.get()
        entry.destroy()

        # Validate the new value (ensure it's a number)
        try:
            new_value = float(new_value)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")
            return

        # Update the Treeview and current_clusters
        values = list(tree_clusters.item(row_id, "values"))
        values[editable_index] = new_value
        tree_clusters.item(row_id, values=values)

        # Update the current_clusters data
        connection_name = values[0]
        for cluster in current_clusters:
            if cluster["Connection Name"] == connection_name:
                if editable_index == 2:
                    cluster["X Coordinate"] = new_value
                elif editable_index == 3:
                    cluster["Y Coordinate"] = new_value
                elif editable_index == 4:  # Added check for Z Coordinate
                    cluster["Z Coordinate"] = new_value

    # Bind the Entry widget to save the edit when the user presses Enter or clicks elsewhere
    entry.bind("<Return>", save_edit)
    entry.bind("<FocusOut>", save_edit)
    entry.focus()


# Bind double-click to enable editing in the clusters Treeview
tree_clusters.bind("<Double-1>", edit_cluster)


# Function to display gates in the second Treeview
def display_gates(gates):
    for row in tree_gates.get_children():
        tree_gates.delete(row)

    for gate in gates:
        origin = gate.get('Origin', 'Unknown')
        destination = gate.get('Destination', 'Unknown')
        tree_gates.insert("", "end", values=(gate['Gate Name'], origin, destination))







# Frame for Gates Table
frame_gates = tk.Frame(root)
frame_gates.pack(padx=10, pady=10)

# Treeview for gates (now including Origin and Destination)
columns_gates = ("Gate Name", "Origin", "Destination")
tree_gates = ttk.Treeview(frame_gates, columns=columns_gates, show="headings")
for col in columns_gates:
    tree_gates.heading(col, text=col)
tree_gates.pack()

# Function to extract gate data with "Origin" and "Destination"
def extract_gate_info(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    gates = []
    for connection in root.findall(".//connection[@ref='destination']"):
        path = connection.get('path', "")
        gate_name = os.path.basename(path)  # Extract the last part of the path

        # Patterns for gate connections
        homebrew_to_original = re.search(r"homebrew_connection_ClusterGate(\d+)to(\d+)", gate_name)
        original_to_homebrew = re.search(r"connection_HBClusterGate(\d+)To(\d+)", gate_name)
        original_to_original = re.search(r"ClusterGate(\d{3})To(\d{3})", gate_name)

        if homebrew_to_original:
            origin = f"HB{int(homebrew_to_original.group(1))}"  # Normalize homebrew
            destination = str(int(homebrew_to_original.group(2)))  # Normalize original
        elif original_to_homebrew:
            origin = str(int(original_to_homebrew.group(2)))  # Normalize original
            destination = f"HB{int(original_to_homebrew.group(1))}"  # Normalize homebrew
        elif original_to_original:
            origin = normalize_cluster_name(f"Cluster_{int(original_to_original.group(1))}_connection")  # Apply normalization
            destination = normalize_cluster_name(f"Cluster_{int(original_to_original.group(2))}_connection")
        else:
            origin, destination = "Unknown", "Unknown"

        gates.append({
            'Gate Name': gate_name,
            'Origin': origin,
            'Destination': destination
        })

    return gates



# Function to display gates with Origin and Destination
def display_gates(gates):
    for row in tree_gates.get_children():
        tree_gates.delete(row)

    for gate in gates:
        # Use a default value if 'Origin' or 'Destination' is not found
        origin = gate.get('Origin', 'Unknown')
        destination = gate.get('Destination', 'Unknown')
        tree_gates.insert("", "end", values=(gate['Gate Name'], origin, destination))


# Function to parse the overwrite XML file
def parse_overwrite_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    new_positions = {}
    # Extract replacement positions
    for replace in root.findall("./replace"):
        sel = replace.get('sel')
        match = re.search(r"connection\[@name='([^']+)'", sel)
        if match:
            connection_name = match.group(1)
            position_elem = replace.find("./offset/position")
            if position_elem is not None:
                x = convert_to_real_number(position_elem.get('x'))
                y = convert_to_real_number(position_elem.get('y'))
                z = convert_to_real_number(position_elem.get('z'))
                new_positions[connection_name] = {'X Coordinate': x, 'Y Coordinate': y, 'Z Coordinate': z}

    return new_positions

def apply_new_positions(new_positions):
    global current_clusters

    for cluster in current_clusters:
        connection_name = cluster['Connection Name']
        if connection_name in new_positions:
            cluster.update(new_positions[connection_name])  # Update the cluster with new X, Y, Z





# Function to convert scientific notation to a standard number
def convert_to_real_number(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return value



# Function to load the overwrite XML and apply changes
def load_overwrite_file():
    file_path = filedialog.askopenfilename(filetypes=[("XML Files", "*.xml")])
    if not file_path:
        messagebox.showinfo("Info", "No file selected!")
        return

    try:
        # Parse the overwrite file
        new_positions = parse_overwrite_file(file_path)

        # Apply new positions to current clusters
        apply_new_positions(new_positions)

        # Refresh the displayed clusters
        display_clusters(current_clusters)

        messagebox.showinfo("Success", "New positions applied to clusters!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


overwrite_button = tk.Button(root, text="Load Overwrite File", command=load_overwrite_file)
overwrite_button.pack(pady=10)



# Run the tkinter event loop
root.mainloop()