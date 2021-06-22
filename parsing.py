"""
Functions used in Rotapy involving the parsing of user-based data.

yes_no: Returns True if Yes, False if No

make_choice_list: Prints a prompt and a list of choices for the user to select
                  from, and returns the user's selection. From a list.

make_choice_dict: Prints a prompt and a list of choices for the user to select
                  from, and returns the user's selection. From a dictionary.

make_output_folder: Makes a directory in the script location to output the downloaded files

parse_opt_geom_from_log: Given a .log file which contains an optimized geometry,
                         extract the (x,y,z) cartesian coordinates.

write_job_to_com: Takes in a list of atoms and their cartesian coordinates such as in parse_opt_geom_from_log,
                  and saves the coordinates to a .com file.
"""
import re
from os import path, makedirs, getcwd


def yes_no(prompt: str) -> bool:
    """
    Returns True if Yes, False if No.

    Parameters
    ----------
    prompt: The string which is used to get the yes or no response.
            "(y/n): " will be tacked on to this string.

    Returns
    -------
    The boolean of whether or not the user indicated positively.
    """
    yes = ["y", "Y", "Yes", "1"]
    no = ["N", "n", "No", "0"]

    while True:
        done = input(f"{prompt} (y/n): ")
        if done in yes + no:
            break

    return done in yes


def make_choice_list(choices: list[str],
                     prompt: str = "\nSelections: ",
                     ret_num: bool = False):
    """
    Prints a prompt and a list of choices for the user to select from.

    Parameters
    ----------
    choices: List of printable objects for the user to choose from.

    prompt: The question to ask the user prior to showing the list of choices.

    ret_num: Whether to return the index of the choice, rather than the actual item in choices.

    Returns
    -------
    If ret_num == False
        The item in the list which the person selected.

    If ret_num == True
        The index of the user's choice within the list.
    """
    print(prompt)
    for n, item in enumerate(choices):
        print(f"{n + 1}) {item}")

    # Ensure that the input is valid.
    while True:
        try:
            selection = int(input("Select one of the following (ex. 2): "))

            # Check that the selection is within the range of the list.
            assert 1 <= selection <= len(choices)
            chosen = choices[selection - 1]
            break

        except ValueError:
            print("The selection must be an integer.")
        except AssertionError:
            print("The selection is not an option in the list.")
    if ret_num:
        return selection - 1

    return chosen


def make_output_folder(sub: str = "") -> str:
    """
    Makes a directory in the script location to output the downloaded files

    Parameters
    ----------
    sub: The name of the directory to be made.

    Returns
    -------
    dir_path: The directory pointing to :sub:

    """
    # Finds the current directory
    dir_path = getcwd()

    # Makes the path for the new folder
    dir_path = dir_path + fr"\{sub}"

    # If the folder doesn't exist, make it.
    if not path.exists(dir_path):
        try:
            makedirs(dir_path)
        except FileExistsError:
            # Sometimes this error pops when using threading or multiprocessing.
            pass
    return dir_path


def parse_geom_from_log(file: str) -> list:
    """
    Given a .log file which contains an optimized geometry, extract the name and (x,y,z) cartesian coordinates.

    Parameters
    ----------
    file: The name of the file to be parsed.

    Returns
    -------
    [["Atom 1 name", X_coord, Y_coord, Z_coord],
    ["Atom 2 name", X_coord, Y_coord, Z_coord]
    ...]
    """

    # Read the data from the file
    with open(file, "r+") as f:
        lines = f.readlines()  # Caution, files may be very /very/ large.

    # The cartesian data is the only data in the file which contains a \
    result_data = [line for line in lines if "\\" in line]

    # Combine the lines into a single line
    result_string = ""
    for line in result_data:
        result_string += line.replace("\n", "").replace(" ", "")

    # Split the data into the \'ed chunks, and remove everything which isn't the cartesian coordinates
    chunks = result_string.split("\\\\")
    data = chunks[3].split("\\")[1:]  # Ignore the charge/multiplicity

    molecule = []
    for entry in data:
        try:
            a = entry.split(",")
            name = a[0]
            x = float(a[1])
            y = float(a[2])
            z = float(a[3])

            new_entry = [name, x, y, z]
            molecule.append(new_entry)
        except IndexError:
            print(
                "The file was formatted in an unexpected way. "
                "Please send the author a copy of the file you are running."
            )
            # The last item in the list of molecules is sometimes empty
            pass

    return molecule


def parse_geom_from_xyz(file: str) -> list:
    """
    Given an .xyz file, extract the name and (x,y,z) cartesian coordinates for the molecule

    Parameters
    ----------
    file: The name of the file to be parsed.

    Returns
    -------
    [["Atom 1 name", X_coord, Y_coord, Z_coord],
    ["Atom 2 name", X_coord, Y_coord, Z_coord]
    ...]
    """

    # Read the data from the file
    with open(file, "r+") as f:
        lines = f.readlines()  # Caution, files may be very /very/ large.

    atoms = []
    for line in lines[2:]:
        name = line[:2].strip()
        x = float(line[2:17])
        y = float(line[18:32])
        z = float(line[33:47])
        atoms.append([name, x, y, z])

    return atoms


def parse_geom_from_com(file: str) -> list:
    """
    Given a .com file, extract the name and (x,y,z) cartesian coordinates for the molecule

    Parameters
    ----------
    file: The name of the file to be parsed.

    Returns
    -------
    [["Atom 1 name", X_coord, Y_coord, Z_coord],
    ["Atom 2 name", X_coord, Y_coord, Z_coord]
    ...]
    """

    # Read the data from the file
    with open(file, "r+") as f:
        lines = f.readlines()  # Caution, files may be very /very/ large.

    # Explanation of the Regex Pattern: [A-Za-z]{1,2} +[-.\d ]+
    #
    # "[A-Za-z]{1,2}"
    # First give me 1 to 2 letters, either upper or lower case.
    # This will capture the abbreviations of all the elements.
    #
    # " +"
    # Then give me one or more spaces
    # This forces there to be a space between the element and the coordinates
    # Excludes some parts of the % headers
    #
    # "[-.\d ]+"
    # Give me one or more dashes, periods, digits, or spaces.
    # Matches the coordinates after the element name
    #
    pattern = re.compile(r"[A-Za-z]{1,2} +[-.\d ]+")
    matches = re.findall(pattern, "\n".join(lines))

    atoms = []
    for match in matches:
        name = match[:2].strip()
        x = float(match[2:17])
        y = float(match[18:32])
        z = float(match[33:47])
        atoms.append([name, x, y, z])

    return atoms
