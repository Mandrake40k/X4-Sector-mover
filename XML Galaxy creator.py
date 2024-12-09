import json
import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Function to load the JSON file
def load_json_file():
    filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if filepath:
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
            return data
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON file: {str(e)}")
    return None

# Function to save the XML file with pretty formatting
def save_as_xml(xml_data):
    filepath = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")])
    if filepath:
        try:
            # Convert the XML tree to a string
            rough_string = ET.tostring(xml_data, encoding="utf-8")
            # Pretty print using minidom
            parsed = minidom.parseString(rough_string)
            pretty_xml = parsed.toprettyxml(indent="  ")

            # Write the pretty-printed XML to file
            with open(filepath, 'w', encoding="utf-8") as file:
                file.write(pretty_xml)

            messagebox.showinfo("Success", f"XML file saved successfully at {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save XML file: {str(e)}")


# Function to generate XML data based on the JSON input
def generate_xml(data):
    # Creating the root element
    diff = ET.Element("diff")

    # Iterating over clusters to create the XML structure
    for cluster in data["clusters"]:
        connection_name = cluster["Connection Name"]
        x = cluster["X Coordinate"]
        y = cluster["Y Coordinate"]
        z = cluster["Z Coordinate"]

        # Create the 'replace' element
        replace = ET.SubElement(diff, "replace", {
            "sel": f"/macros/macro[@name='XU_EP2_universe_macro']/connections/connection[@name='{connection_name}']/offset"
        })

        # Create the 'offset' element
        offset = ET.SubElement(replace, "offset")

        # Create the 'position' element with coordinates
        position = ET.SubElement(offset, "position", x=str(x), y=str(y), z=str(z))

    return diff

# GUI setup
def create_gui():
    window = tk.Tk()
    window.title("JSON to XML Converter")

    # Load JSON button
    def load_and_generate():
        data = load_json_file()
        if data:
            xml_data = generate_xml(data)
            save_as_xml(xml_data)

    load_button = tk.Button(window, text="Load JSON File", command=load_and_generate)
    load_button.pack(pady=20)

    window.mainloop()

if __name__ == "__main__":
    create_gui()
