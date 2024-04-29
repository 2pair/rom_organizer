from argparse import ArgumentParser, Namespace
from pathlib import Path
from sys import exit


VERBOSE = False


def get_args() -> Namespace:
    """Get command line arguments."""
    parser = ArgumentParser(description="Moves matching files to subdirectories based on the first letter of the file's name")
    parser.add_argument("--dir", required=True, help="The directory where the files are located")
    parser.add_argument("--ext", help="If specified, only files with the given file extension will be moved")
    parser.add_argument("--region", help="If specified, only files with the given region will be moved")
    parser.add_argument("--verbose", "-v", action="store_true", help="If specified, data will be logged to stdout")
    parser.add_argument("--no-warn", action="store_true", help="If specified, program will not confirm before taking action")
    args = parser.parse_args()

    # Add the dot if needed
    if args.ext and args.ext[0] != ".":
        args.ext = "." + args.ext

    return args


class RomOrganizer:
    """Organizes the ROMs in the directory."""
    def __init__(self, directory: Path, extension: str=None, region: str=None):
        self.directory = directory
        self.extension = extension
        self.region = region

    def file_meets_requirements(self, file: Path) -> bool:
        """Checks if the file meets the requirements."""
        if not file.is_file():
            if VERBOSE:
                print(f"Not moving {file.name} because it is not a file")
            return False
        if file.suffix != self.extension:
            if VERBOSE:
                print(f"Not moving {file.name} because it is not a {self.extension} file")
            return False
        if self.region and self.region not in file.stem:
            if VERBOSE:
                print(f"Not moving {file.name} because the name did not contain {self.region} region")
            return False
        return True

    def get_output_dir_name(self, filename: str) -> str:
        """Get the name of the output directory for the given file."""
        first_char = filename[0]
        if first_char.isdigit():
                return "0"
        if first_char.isalpha():
                return first_char
        return "_"

    def run(self) -> None:
        """Organizes the ROMs"""
        print(f"Organizing ROMs in {self.directory}")
        for item in sorted(self.directory.iterdir(), key=lambda p: p.name.lower()):
            if not self.file_meets_requirements(item):
                continue
            output_dir_name = self.get_output_dir_name(item.stem)
            if VERBOSE:
                print(f"Moving {item.name} to output_dir_name")
            output_dir = self.directory.joinpath(output_dir_name)
            output_dir.mkdir(exist_ok=True)
            item.rename(output_dir.joinpath(item.name))
        print("Done")
    
      

if __name__ == "__main__":
    try:
        args = get_args()
        if args.verbose:
            VERBOSE = args.verbose
        directory = Path(args.dir)
        if not args.no_warn:
            print(f"All *{args.ext} files in \"{directory.absolute()}\" will be moved. Are you sure? (y/N)")
            while True:
                choice = input()
                if not choice or choice.lower() == "n":
                    print("User aborted")
                    exit(0)
                elif choice.lower() == "y":
                    break
                else:
                    print("Please enter 'y' or 'n'")
        rom_organizer = RomOrganizer(directory, args.ext, args.region)
        rom_organizer.run()
    except KeyboardInterrupt:
        print("User requests exit")    
    exit(0)
