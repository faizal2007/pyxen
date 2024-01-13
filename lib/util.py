import random
import string
import os, glob

def generate_password(length=12):
    characters = string.ascii_letters + string.digits  # Only letters and digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def convert_ram(value_in_bytes):
    units = ['MB', 'GB', 'TB']
    index = 0
    bytes_value = float(value_in_bytes)

    while bytes_value >= 1024 and index < len(units) - 1:
        bytes_value /= 1024
        index += 1

    return f"{bytes_value:.2f} {units[index]}"

def log_cleanup(file_pattern):
    logs = glob.glob(file_pattern)

    # Loop through the matching files and delete them
    for file_path in logs:
        try:
            os.remove(file_path)
            print(f"Cleaning up : {file_path}")
        except OSError as e:
            print(f"Error cleaning up {file_path}: {e}")
    
def convert_to_short_form(size):
    if size.endswith(" GiB"):
        return size.replace(" GiB", "G")
    elif size.endswith(" MiB"):
        return size.replace(" MiB", "M")
    elif size.endswith(" TiB"):
        return size.replace(" TiB", "T")
    else:
        return size  # Return unchanged if not GiB, MiB, or TiB
