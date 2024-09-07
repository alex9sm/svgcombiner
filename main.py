import os
import xml.etree.ElementTree as ET
import re

def extract_number(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else float('inf')

def convert_to_pixels(value):
    if isinstance(value, (int, float)):
        return float(value)
    match = re.match(r"([\d.]+)(\w+)?", value)
    if not match:
        return 100.0  # default value
    number, unit = match.groups()
    number = float(number)
    if unit == "pt":
        return number * 1.33333
    elif unit == "pc":
        return number * 16
    elif unit == "mm":
        return number * 3.77952756
    elif unit == "cm":
        return number * 37.7952756
    elif unit == "in":
        return number * 96
    else:
        return number

def get_svg_dimensions(svg):
    width = svg.get('width')
    height = svg.get('height')
    if width is None or height is None:
        viewBox = svg.get('viewBox')
        if viewBox:
            _, _, width, height = map(float, viewBox.split())
    return convert_to_pixels(width), convert_to_pixels(height)

def combine_svgs(input_folder, output_file, global_margin=10, custom_margins=None):
    root = ET.Element('svg', xmlns="http://www.w3.org/2000/svg")
    
    svg_files = sorted(
        [f for f in os.listdir(input_folder) if f.endswith('.svg')],
        key=extract_number
    )
    
    elements = []
    for i, filename in enumerate(svg_files):
        filepath = os.path.join(input_folder, filename)
        tree = ET.parse(filepath)
        svg = tree.getroot()
        width, height = get_svg_dimensions(svg)
        custom_margin = custom_margins.get(i, {}) if custom_margins else {}
        left_margin = custom_margin.get('left', global_margin)
        right_margin = custom_margin.get('right', global_margin)
        top_margin = custom_margin.get('top', global_margin)
        bottom_margin = custom_margin.get('bottom', global_margin)
        elements.append((svg, width, height, left_margin, right_margin, top_margin, bottom_margin))

    # Define the distribution of elements per line
    line_distribution = [1, 1, 3, 6, 8, 8, 8, 9, 9]  # Distributed across 9 lines
    
    max_width = 0
    max_height_per_line = []
    start_index = 0

    for count in line_distribution:
        line_elements = elements[start_index:start_index + count]
        line_width = sum(width + left_margin + right_margin for _, width, _, left_margin, right_margin, _, _ in line_elements)
        max_width = max(max_width, line_width)
        max_height_per_line.append(max(height + top_margin + bottom_margin for _, _, height, _, _, top_margin, bottom_margin in line_elements))
        start_index += count

    total_height = sum(max_height_per_line)

    root.set('width', str(max_width))
    root.set('height', str(total_height))

    y_offset = 0
    start_index = 0

    for i, count in enumerate(line_distribution):
        line_elements = elements[start_index:start_index + count]
        x_offset = 0

        for svg, width, height, left_margin, right_margin, top_margin, bottom_margin in line_elements:
            x_offset += left_margin
            group = ET.SubElement(root, 'g', transform=f"translate({x_offset},{y_offset + top_margin})")
            for element in svg:
                group.append(element)
            x_offset += width + right_margin

        y_offset += max_height_per_line[i]
        start_index += count

    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    input_folder = 'input'
    output_file = 'output/combined.svg'
    global_margin = 10  # Global margin for all elements

custom_margins = {
    0: {'left': 100, 'top': 100},
    1: {'left': 100},
    2: {'right': 0, 'left': 100},
    3: {'left': 100},  
    5: {'left': 100},
    11: {'left': 100},
    19: {'left': 100},
    27: {'left': 100},
    35: {'left': 100},
    44: {'left': 100},
}

combine_svgs(input_folder, output_file, global_margin, custom_margins)