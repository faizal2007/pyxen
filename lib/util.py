import random
import string

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
