"""File for Interface to receive and parse command line arguments"""
from typing import Dict, List, Any
from sys import argv
from pathlib import Path



class IncludesGraphCmdLineParsingError(Exception):
    """The base of all Errors from command Line parsing in Includes Graph"""


class ParamParser:
    """Interface to receive and parse command line arguments"""

    args: List[str]
    options: List[str]
    flags: Dict[str, Any]
    dirs: List[Path]

    possible_options: List[Dict[str, Any]]
    possible_flags: List[Dict[str, Any]]

    def __init__(self):

        self.populate_possibles()
        self._cmd_to_list(argv)
        self._parse_options()
        self._parse_flags()
        self._parse_dirs()

    def _cmd_to_list(self, cli_args: List[str]) -> None:
        """Read arguments from command line and return a List string iterable"""
        self.args = cli_args

    def _parse_options(self) -> None:
        """Pull options from args"""
        self.options = [opt for opt in self.args if opt.count("-") == 1 and opt.startswith("-")]
        for opt in self.options:
            self.args.remove(opt)

    def _parse_flags(self) -> None:
        """Pull flags from args"""
        args = self.args.__iter__()
        while 1:
            try:
                arg = next(args)
                if arg in self.possible_flags:
                    self.flags[arg] = None if "val" not in self.flags.values() else next(args)
            except StopIteration:
                break
        for key, val in self.flags.items():
            self.args.remove(key)
            if val:
                self.args.remove(val)

    def _parse_dirs(self) -> None:
        """Parse directories from the command line args"""
        self.dirs = [Path(_dir) for _dir in self.args if Path(_dir).is_dir()]

    def _check_args_parsed(self) -> None:
        if len(self.args) > 0:
            raise IncludesGraphCmdLineParsingError(
                f"Expected all aguments to have been parsed but found {self.args}"
            )

    def populate_possibles(self) -> None:
        """Generate all the possible values that can be passed through CLI"""
        self.possible_options.extend([{
            "-o": {
                "arg": "dependency_tree",
                "arg_req": True,
                "description": "Pass the specific name of the outputted image file",
                "usage": "-o <file_name>",
                "example": "ig <dirs> -o test -> test.pdf"
            },
            "-F": {
                "arg": "pdf",
                "arg_req": True,
                "description": "Pass specific file type output image will take",
                "usage": "-F <file_ending>",
                "example": "ig <dirs> -F png -> <file?.png"
            },
            "-U": {
                "arg": Path,
                "arg_req": True,
                "description": "Pass specific path to existing dot/json file denoting dependency image",
                "usage": "-U <file>",
                "example": "ig -U example.dot -> *Generates dependency_tree.pdf*"
            }

        }])
        self.possible_flags.extend(([{
            "--output": {
                "arg": "dependency_tree",
                "arg_req": True,
                "description": "Pass specific name output image file",
                "usage": "--output <file_name>",
                "example": "ig <dirs> -o test -> test.pdf"
            },
            "--file-type": {
                "arg": "pdf",
                "arg_req": True,
                "description": "Pass specific file type output image will take",
                "usage": "--file-type <file_ending>",
                "example": "ig <dirs> -F png -> <file?.png"
            },
            "--use-existing": {
                "arg": "compile-command.json",
                "arg_req": True,
                "description": "Pass specific path to existing dot/json file denoting dependency image",
                "usage": "--use-existing <file>",
                "example": "ig --use-existing example.dot -> *Generates dependency_tree.pdf*"
            }
        }]))
