from argparse import ArgumentParser, Namespace
from pathlib import Path
from sys import exit


VERBOSE = False


def get_args() -> Namespace:
    """Get command line arguments."""
    parser = ArgumentParser(
        description="Moves matching files to subdirectories based on the first letter of the file's name"
    )
    parser.add_argument(
        "--dir", required=True, help="The directory where the files are located"
    )
    parser.add_argument(
        "--ext",
        help="If specified, only files with the given file extension will be moved",
    )
    parser.add_argument(
        "--region", help="If specified, only files with the given region will be moved"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="If specified, data will be logged to stdout",
    )
    parser.add_argument(
        "--no-warn",
        action="store_true",
        help="If specified, program will not confirm before taking action",
    )
    args = parser.parse_args()

    # Add the dot if needed
    if args.ext and args.ext[0] != ".":
        args.ext = "." + args.ext

    return args


class RomOrganizer:
    """Organizes the ROMs in the directory."""

    def __init__(
        self,
        directory: Path,
        extension: str = None,
        region: str = None,
        confirm: bool = False,
    ):
        self.directory: Path = directory
        self.extension: str = extension
        self.region: str = region
        self.confirm: bool = confirm

        if not self.directory.is_dir():
            raise ValueError(f"{self.directory} is not a directory")

    def file_meets_requirements(self, file: Path) -> bool:
        """Checks if the file meets the requirements."""
        if not file.is_file():
            if VERBOSE:
                print(f"Not moving {file.name} because it is not a file")
            return False
        if file.suffix.lower() != self.extension.lower():
            if VERBOSE:
                print(
                    f"Not moving {file.name} because it is not a {self.extension} file"
                )
            return False
        parts = file.stem.split(sep="(", maxsplit=1)
        search_space = parts[1] if len(parts) > 1 else parts[0]
        if self.region and self.region.lower() not in search_space.lower():
            if VERBOSE:
                print(
                    f"Not moving {file.name} because the name did not contain {self.region} region"
                )
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

    def get_files(self) -> dict[str, list[Path]]:
        """Gets all the files that will be moved.

        Returns:
            All of the files that will be moved, keyed by output directory names.
        """
        files = {}
        for item in sorted(self.directory.iterdir(), key=lambda p: p.name.lower()):
            if not self.file_meets_requirements(item):
                continue
            output_dir_name = self.get_output_dir_name(item.stem)
            dir_files = files.setdefault(output_dir_name, [])
            dir_files.append(item)
        return files

    def move_files(self, files_by_directory: [str, list[Path]]) -> None:
        """Moves the listed files to the directory named by 'key'."""
        for dir_name, dir_files in files_by_directory.items():
            for file in dir_files:
                if VERBOSE:
                    print(f"Moving {file.name} to output_dir_name")
                output_dir = self.directory.joinpath(dir_name)
                output_dir.mkdir(exist_ok=True)
                file.rename(output_dir.joinpath(file.name))


    def run(self) -> None:
        """Organizes the ROMs."""
        print(f"Organizing ROMs in {self.directory}")
        files = self.get_files()
        if not files:
            print("No files found")
            return
        if self.confirm and not confirm_prompt(
            f"{sum(len(dir_files) for dir_files in files.values())} files will be moved. continue?",
            True,
        ):
            print("User aborted")
            return
        
        self.move_files(files)
        print("Done")


def confirm_prompt(question: str, default: bool = True) -> bool:
    y = "Y" if default else "y"
    n = "N" if not default else "n"
    print(f"{question} ({y}/{n})")
    while True:
        choice = input()
        if (not default and not choice) or choice.lower() == "n":
            return False
        elif (default and not choice) or choice.lower() == "y":
            return True
        else:
            print("Please enter 'y' or 'n'")


if __name__ == "__main__":
    try:
        args = get_args()
        if args.verbose:
            VERBOSE = args.verbose
        directory = Path(args.dir)
        if not args.no_warn:
            if not confirm_prompt(
                f'All *{args.ext} files in "{directory.absolute()}" will be moved. Are you sure?',
                False,
            ):
                print("User aborted")
                exit(0)
        rom_organizer = RomOrganizer(directory, args.ext, args.region, not args.no_warn)
        rom_organizer.run()
    except KeyboardInterrupt:
        print("User requests exit")
    exit(0)
