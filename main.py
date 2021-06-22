"""
@Author: Jackson K Elowitt
@Start Date: May 14, 2021
@Contact: jkelowitt@protonmail.com
@Site: https://github.com/jkelowitt/GenerateFigureFromFile
"""
from glob import glob

from classes import Molecule, Atom
from functions import verified_input, show_structure, save_structure
from parsing import parse_geom_from_log, parse_geom_from_xyz, parse_geom_from_com, yes_no


def make_molecule_from_file(file, directory):
    parsing_dict = {
        "log": parse_geom_from_log,
        "xyz": parse_geom_from_xyz,
        "com": parse_geom_from_com
    }

    name_xyz = parsing_dict[file[file.index(".") + 1:]](file)
    atoms = [Atom(a[0], (a[1], a[2], a[3])) for a in name_xyz]
    molecule_name = file[len(directory):]
    molecule = Molecule(molecule_name, atoms)

    return molecule


def main():
    files = []
    directory = ""
    parsing_dict = {
        "log": parse_geom_from_log,
        "xyz": parse_geom_from_xyz,
        "com": parse_geom_from_com
    }

    while not files:
        # Get the directory from the user
        print("\nEnter the directory which contains one of the following files.")
        print("Valid file types:")
        for ext in parsing_dict:
            print(f"\t.{ext}")
        directory = input("Directory: ")

        # Get all the files
        # which have a parsing function.
        for ext in parsing_dict:
            files += glob(f"{directory}/*.{ext}")

        files.sort(key=lambda x: len(x))

        # Check that there are valid files to be found.
        if not files:
            print("\nNo valid files found in the selected directory.")

    output_dir = input("What would you like to name the folder which will hold the figures: ")

    print("\nYou will be asked for an Azimuth and an Elevation.")
    print("These values can be found in the bottom right of the interactive view.\n")
    show_example = yes_no("Show an interactive sample")

    if show_example:
        molecule = make_molecule_from_file(files[0], directory)
        show_structure(molecule, title=molecule.name, azi=10, ele=10)

    azimuth = verified_input("Choose the Azimuth: ", verify=float)
    degree = verified_input("Choose the Elevation: ", verify=float)

    # Select the parsing function based on the extension, then parse.
    for file in files:
        molecule = make_molecule_from_file(file, directory)
        save_structure(molecule, output=output_dir, azi=azimuth, ele=degree)


if __name__ == "__main__":
    print("GenerateFigureFromFile".center(50, "~"))
    print("Author: Jackson Elowitt")
    print("Repo: https://github.com/jkelowitt/GenerateFigureFromFile")
    print("Version: v1")
    print("".center(50, "~"))

    main()

    input("\nFigures saved to the .exe's location. Press enter to close. ")
