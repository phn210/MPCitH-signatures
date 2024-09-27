import os
import re

def generate_pxd_for_pyx(pyx_file):
    """
    Generates a .pxd file for the given .pyx file.
    Extracts all cdef and cpdef function/class declarations.
    """
    pxd_file = pyx_file.replace(".pyx", ".pxd")
    
    with open(pyx_file, 'r') as f:
        pyx_content = f.readlines()

    pxd_lines = []
    
    # Regex to detect the start of a cdef or cpdef function or class declaration
    func_pattern = re.compile(r'^\s*(cdef|cpdef)\s+')
    
    inside_declaration = False  # Flag to track if we're inside a multi-line declaration
    current_declaration = []  # List to store multi-line declaration
    
    # Loop through each line in the pyx file
    for line in pyx_content:
        # If we're inside a declaration, keep appending lines until we reach the end
        if inside_declaration:
            current_declaration.append(line)
            if line.strip().endswith(":"):  # End of function or class declaration
                inside_declaration = False
                pxd_lines.append("".join(current_declaration))  # Join lines and add to the pxd content
                current_declaration = []
        else:
            # Start of a new cdef/cpdef function or class declaration
            match = func_pattern.match(line)
            if match:
                inside_declaration = True
                current_declaration.append(line)
    print(pxd_lines)
    
    # Write the extracted lines to the .pxd file
    if pxd_lines:
        with open(pxd_file, 'w') as f:
            f.write("# Automatically generated .pxd file for {}\n".format(os.path.basename(pyx_file)))
            f.writelines(pxd_lines)
        print(f"Generated {pxd_file}")
    else:
        print(f"No cdef/cpdef functions or classes found in {pyx_file}, skipping .pxd generation.")


def generate_pxd_for_all_pyx(directory):
    """
    Scans the directory for .pyx files and generates .pxd files for each one.
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".pyx"):
                pyx_file = os.path.join(root, file)
                # print(pyx_file)
                generate_pxd_for_pyx(pyx_file)

if __name__ == "__main__":
    # Replace 'your_directory' with the path where your .pyx files are located
    directory = "."
    print('Generating .pxd files for all .pyx files in the directory...')
    generate_pxd_for_all_pyx(directory)
    print('Done')
