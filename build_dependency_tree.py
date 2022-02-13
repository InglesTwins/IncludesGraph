"""Main file to extract dependencies to model the include graph"""

import sys
import re
from pathlib import Path
from typing import Optional, Union
from typing import List, Dict


def extract_files_from_directory():
    """FUnction recurses through the directory to find all file-like objects"""

    def is_cpp_file(file: Union[Path, str]):
        file_types = ('.c', '.cpp', '.cxx', '.C', '.h', '.hpp', '.hxx')
        return_value = False
        for file_type in file_types:
            return_value = return_value or file_type in str(file)
            if return_value:
                return True
        return False

    def extract_files(dir_or_file: Path, list_o_files: List[Optional[Path]]):
        if dir_or_file.is_dir():
            print(f'In dir: {str(dir_or_file.absolute())}')
            for path in dir_or_file.glob("*"):
                extract_files(path, list_o_files)
        else:
            if is_cpp_file(dir_or_file.name):
                print(f'Appending file: {str(dir_or_file.absolute())}')
                list_o_files.extend([dir_or_file])
        return list_o_files

    def flatten_list(lists: Optional[List[List]]):
        return [
                item for sublist in lists for item in sublist
                if len(sublist) > 0]

    return flatten_list(
            [extract_files(Path(arg), []) for arg in sys.argv])


# I think we can get rid of thise function
def separate_headers_and_implementations(files_in_dir: List[Path]):
    """
    Separates files from current directory into header and implementation files

    :param files_in_dir:    List of paths to files C++ files in current
                            directory
    return: returns:        tuple of list containing paths to the header files
                            in first slot and implementation files in the
                            second
    """
    headers = [file for file in files_in_dir if file.suffix in ('h', 'hpp')]
    impls = [file for file in files_in_dir if file.suffix in ('c', 'cpp')]
    return headers, impls


# NOTE: Do we want to make re.Pattern object a function parameter?
# KI: No, but also don't want it to be a global variable. This screams classes
#
# Pattern object to match either `<...>` or `"..."`
include_statement_pattern = re.compile(r"(<.+?>)|(\".+?\")")


def create_single_file_dependency_list(file: Union[Path, str]):
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
    # For some reason does not drop the <> or " when matching
    # so we write a helper
    def extract_header_file_name(text: Optional[str]):
        if text:
            return text[1:len(text)-1]
        else:
            return None

    with open(str(file.absolute())) as f:
        # some files may have macros that check for operatoring system or
        # compiler compatibilities. For now we ignore these as well.
        # We also need to ignore include statements made in comments
        include_statements = []
        b_is_block_comment = False  # Lines that start with /*
        for line in f.readlines():
            print(f"{line.strip()}")
            if b_is_block_comment and '*/' in line:
                b_is_block_comment = False
            elif line.replace(' ', '')[0:2] == '//':
                continue
            elif not line:  # empty line
                continue
            elif line.replace(' ', '').startswith('#include') or \
                    line.replace(' ', '').startswith('%:include'):
                # we always expect the included file to be given second
                # (required by standards)
                re_match = include_statement_pattern.search(line)
                # We only expect one entry in the list
                if not re_match:  # first matching group is empty
                    print(f'No header files found in line: {line}')
                    continue
                elif not re_match.group(1):
                    # Check if match with `<...>` is None
                    print(f"""Header file found
                            {str(file.absolute())}:{re_match.group(2)}""")
                    include_statements.append(
                            extract_header_file_name(
                                re_match.group(2)))
                else:
                    # since we have a match and first group is non-empty we
                    # apend
                    print(f"""Header file found
                            {str(file.absolute())}:{re_match.group(1)}""")
                    include_statements.append(
                            extract_header_file_name(
                                re_match.group(1)))
        return include_statements


def output_dependency_tree_to_dot_file(
        dep_tree: Dict[List[Union[Path, str]], str],
        output_name: Optional[Union[Path, str]]):
    """
    Goes through dictionary of files gathered from recursive search of
    directory and prints all the nodes it will be attached to in file
    named output_name.
    Output is formated to be compatible with the DOT command line program:
    https://graphviz.org/doc/info/lang.html

    :param dep_tree:    dictionary with files in project as keys and list
                        of their dependencies as value
    :param output_name: name of output file or path to output file
    """
    if not isinstance(dep_tree, dict):
        # For cleaner debugging messages, only keep while still developing
        # program
        print("None dictionary object passed. Exiting...")
        quit()

    if not output_name:
        output_name = Path('./includes_tree_output.dot').absolute()

    print(f'Output file is: {str(output_name)}')

    # TODO: Need to colorize output.
    #       E.g. header files are blue, translation units red
    #       Standard Template Library files are different shaped bubbles, etc
    #       Of course this will require a key of some sort to be documentd
    #       somewhere
    with open(str(output_name.absolute()), 'w') as f:
        f.write("graph {\n")
        _ = [[
            f.wtite(f'"{key}" -- "{entry}";\n') 
            for entry in dep_list] 
            for key, dep_list in dep_tree.items()]
        f.write("}")


def generate_dependency_tree(
        files_in_project: List[Path],
        keep_std_files: bool = True):
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
    for child in pwd.glob("util/*"):
        with open(f"{pwd}/{child}", 'r') as f:
            std_files = [
               line.strip()
               for line in f.readlines()
               if line
               ]  # strip to remove '\n' char
    return {
        str(file): create_single_file_dependency_list(file)
        for file in files_in_project
        if file not in std_files or keep_std_files
    }
