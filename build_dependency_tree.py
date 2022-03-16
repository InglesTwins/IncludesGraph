"""Main file to extract dependencies to model the include graph"""

import sys
import re
from pathlib import Path
from typing import Optional, Union
from typing import List, Dict, Set, Tuple
from io import TextIOWrapper

# TODO: Move current print statements to a log output file
# TODO: Use uniform function argument list style
# TODO: Use pathlib.relative_to function to output .DOT file with
#       with shorter names. This means we have to keep the "project"
#       stored somewhere
# TODO: Check iterative directory search when collecting cpp files

# IDEA: We can keep the entire directory structure stored for the project
#       and then determine a metric to compare how well a given file matches
#       with a file of the same name in multiple directories


class CppFileObject():  # FIXME: I belong in a separate file
    """
    This acts simply as a way to encapsulate cpp files
    Cpp files are distinguished by the path to the file.
    This helps resolve ambiguities for files with the same name but in
    different directories when making the dependency tree
    """

    def __init__(self, path_to_file: Path, file_name: str) -> None:
        self.path_to_file = path_to_file
        self.file_name = file_name

    def open(self) -> TextIOWrapper:
        return open(str(self.path_to_file) + '/' + self.file_name, 'r')

    def __repr__(self):
        return str(self.path_to_file / self.file_name)


def extract_files_from_directory(
        set_o_dirs: Set[Path]) -> Tuple[Set[CppFileObject], Set[Path]]:
    """
    TODO: Improve function description
    Function recurses through the directory to find all file-like objects
    """

    def is_cpp_file(file: Union[Path, str]) -> bool:
        file_types = ('.c', '.cc', '.cpp', '.cxx', '.c++', '.C',
                      '.h', '.hh', '.hpp', '.hxx', '.h++', '.H')
        return_value = False
        for file_type in file_types:
            return_value = return_value or file.endswith(file_type)
            if return_value:
                return True
        return False

    def extract_files(dir_or_file: Path,
                      set_o_files: Set[CppFileObject]
                      ) -> Set[CppFileObject]:
        if dir_or_file.is_dir():
            # print(f'In dir: {str(dir_or_file.absolute())}')
            for path in dir_or_file.glob("*"):
                extract_files(path, set_o_files)
        else:
            if is_cpp_file(dir_or_file.name):
                # print(f'Appending file: {str(dir_or_file.absolute())}')
                temp_obj = CppFileObject(dir_or_file.parent, dir_or_file.name)
                print(str(temp_obj))
                set_o_files.update([temp_obj])
        return set_o_files

    def flatten_set(
                     lists: Optional[Set[CppFileObject]]
                     ) -> List[CppFileObject]:
        return (item for sublist in lists for item in sublist
                if len(sublist) > 0)

    # We want to keep track of how to get to the file
    # therefore we keep the path to the file
    return flatten_set(
            [extract_files(Path(directory), set())
             for directory in set_o_dirs]), set_o_dirs


# NOTE: Do we want to make re.Pattern object a function parameter?
# KI: No, but also don't want it to be a global variable. This screams classes
#
# Pattern object to match either `<...>` or `"..."`
include_statement_pattern = re.compile(r"(<.+?>)|(\".+?\")")


def create_single_file_dependency_list(
        file: CppFileObject
     ) -> Set[CppFileObject]:
    """
    Go through header files and implementation files and scan for `#include`
    keyword, then maybe some regex to extract the file name.
    For each file we go through, we create a list of the files required by
    it.

    With C++20 and C++23 we will have to include import statements as well
    But we leave this for future work

    :param file:        path to C++ file in current project
    :returns:    a list of the files that `file` depends on
    """

    with file.open() as f:
        # some files may have macros that check for operatoring system or
        # compiler compatibilities. For now we ignore these as well.
        # We also need to ignore include statements made in comments
        include_statements = set()
        b_is_block_comment = False  # Lines that start with /*
        for line in f.readlines():
            if b_is_block_comment and line.endswith('*/'):
                b_is_block_comment = False
            elif line.startswith('//') or not line:
                continue
            elif line.replace(' ', '').startswith('#include') or \
                    line.replace(' ', '').startswith('%:include'):

                re_match = include_statement_pattern.search(line)

                # Split header on '/' to determine if it is in its parent
                # directory

                if not re_match:  # no matches found
                    continue
                elif not re_match.group(1):
                    # Check if match with `<...>` is None
                    print(f"""Header file found
                            {str(file)}:{re_match.group(2)}""")
                    included_file = re_match.group(2)[1:-1]
                else:
                    # since we have a match and first group is non-empty we
                    # append
                    print(f"""Header file found
                            {str(file)}:{re_match.group(1)}""")
                    included_file = re_match.group(1)[1:-1]

                included_file = included_file.split('/')
                if len(included_file) == 1:
                    # TODO: Check that file is not std header
                    include_statements.update(
                        [CppFileObject(file.path_to_file.absolute(),
                                       '/'.join(included_file))])
                elif '..' in included_file:
                    print(f"""No relative path searches provided yet
                              {'/'.join(included_file)}""")
                    cfo = CppFileObject(file.path_to_file.absolute(),
                                        '/'.join(included_file))
                    include_statements.update([cfo])
                else:
                    # We assume the provided path starts from the project
                    # top directory
                    path_to_file = Path('/'.join(included_file[:-1]))
                    file_name = included_file[-1]
                    include_statements.update(
                        [CppFileObject(Path(path_to_file),
                                       file_name)])
    return include_statements


def output_dependency_tree_to_dot_file(
        dep_tree: Dict[Union[Path, str], Set[CppFileObject]],
        set_o_dirs: Set[Path],
        output_name: Optional[Union[Path, str]]) -> None:
    """
    Goes through dictionary of files gathered from recursive search of
    directory and prints all the nodes it will be attached to in file
    named output_name.
    Output is formated to be compatible with the DOT command line program:
    https://graphviz.org/doc/info/lang.html

    :param dep_tree:    dictionary with files in project as keys and list
                        of their dependencies as value
    :param set_o_dirs:  the dirs traversed to find all header files, used
                        to shorten the names of outputted strings in dot 
                        file
    :param output_name: name of output file or path to output file
    """
    if not isinstance(dep_tree, dict):
        # For cleaner debugging messages, only keep while still developing
        # program
        print("None dictionary object passed. Exiting...")
        quit()

    # FIXME: I should accept costum path
    if not output_name:
        output_name = Path('./includes_tree_output.dot').absolute()

    # TODO: Need to colorize output.
    #       E.g. header files are blue, translation units red
    #       Standard Template Library files are different shaped bubbles, etc
    #       Of course this will require a key of some sort to be documentd
    #       somewhere
    def dir_rep(path: CppFileObject, set_o_dirs: Set[Path]) -> str:
        for d in set_o_dirs:
            path = str(path).replace(str(d.absolute()), '')
        return path
    with open(str(output_name.absolute()), 'w') as f:
        f.write("graph {\n")
        _ = [[f.write(f'''\t"{dir_rep(key, set_o_dirs)}"
                          -- "{dir_rep(entry, set_o_dirs)}";\n''')
              for entry in dep_list]
             for key, dep_list in dep_tree.items()]
        f.write("}")


def generate_dependency_tree(
        files_in_project: Set[CppFileObject],
        keep_std_files: bool = True
     ) -> Dict[CppFileObject, Set[CppFileObject]]:
    """
    Creates a dictionary with file name as key and its dependency tree as the
    value

    :param files_in_project:    all C++ files in provided directory and
                                subdirectories
    :param keep_std_files:      flag to determine whether to track C/C++
                                standarad
                                files

    :returns return: dictionary of files which project specific files depend on
    """
    pwd = Path(__file__).absolute().parent
    with open(f"{str(pwd)}/util/C_std_headers.txt", 'r') as f:
        std_files = [
                line.strip()
                for line in f.readlines()
                if line
                ]  # strip to remove '\n' char
    with open(f"{str(pwd)}/util/Cpp_std_headers.txt", 'r') as f:
        std_files.extend([
                line.strip()
                for line in f.readlines()
                if line])

    def match_headers_with_found_headers(
            dependency_tree: Dict[str, List[str]]
         ) -> Dict[str, str]:
        """Helper function to avoid file duplication in dependency tree"""
        set_of_headers = set()
        for key, value in dependency_tree.items():
            if len(value) != 0:
                set_of_headers.update([entry for entry in value])

        # quit()
        print(set_of_headers)

        # conversion to header files as they actually appear in code
        key_for_headers = {}
        for key in dependency_tree.keys():
            print(f"Comparing file: {key}")
            if '.c' in str(key).lower():
                print("File is a translation unit")
                key_for_headers[str(key)] = str(key)
            else:
                b_matched = False
                for header in set_of_headers:
                    if str(key).endswith(str(header)):
                        # Seems we need to create some sort of class that
                        # stores whether a specific header has already been
                        # matched
                        b_matched = True
                        print("File matched to existing header")
                        if str(key) in key_for_headers:
                            print(f"""Header file {key} is duplicated, previous
                                  value has been overwitten""")
                        key_for_headers[str(key)] = \
                            str(key)[-len(str(header)):]
                if not b_matched:
                    print(f"File: {key} not matched to any include statement")
                    key_for_headers[str(key)] = str(key)

        return key_for_headers

    temp_dict = dict(
                (str(file), create_single_file_dependency_list(file))
                for file in files_in_project
                if file not in std_files
                or keep_std_files  # complicated logic
            )
    converter = match_headers_with_found_headers(temp_dict)
    return dict(
            (converter[str(key)], temp_dict[str(key)])
            for key in temp_dict.keys()
            # only keep track of headers actually used
            if str(key) in converter.keys())
