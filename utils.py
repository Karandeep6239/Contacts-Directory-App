import os
from termcolor import colored

def get_int_range(min: int, max: int) -> int:
    """Returns a integer between given min and max range."""
    while True:
        try:
            choice = int(input())
            if choice < min or choice > max:
                print(colored(f"Error: Input must be between range {min} & {max}.", "red"))
            else:
                return choice
        except ValueError:
            print(colored("Error: Enter a valid Integer.", "red"))

def clear_screen() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')