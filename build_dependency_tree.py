"""Main file to extract dependencies to model the include graph"""

import sys
import re
from pathlib import Path
from typing import Optional
<<<<<<< HEAD
from typing import List
=======
from typing import List, Dict
>>>>>>> Generate Project Dependencies


def extract_files_from_directory():
    """FUnction recurses through the directory to find all file-like objects"""

    def extract_files(dir_or_file: Path, list_o_files: List[Optional[Path]]):
        if dir_or_file.is_dir():
            for path in dir_or_file.glob("*"):
                extract_files(path, list_o_files)
        else:
            list_o_files.append(dir_or_file)

    return [extract_files(Path(arg), []) for arg in sys.argv]


def separate_headers_and_implementations(files_in_dir: List[Path]):
    """ 
    Separates files from current directory into header and implementation files.
    
    :param files_in_dir: List of paths to files C++ files in current directory
    
    return: returns: tuple of list containing paths to the header files in 
    first slot and implementation files in the second
    """
    headers = [file for file in files_in_dir if file.suffix in ('h', 'hpp')]
    impls = [file for file in files_in_dir if file.suffix in ('c', 'cpp')]
    return headers, impls


# NOTE: Do we want to make re.Pattern object a function parameter?
# KI: No, but also don't want it to be a global variable. This screams classes
#
# match either the pattern `<...>` or `"..."`
include_statement_pattern = re.compile
def create_single_file_dependency_list(file: Union[Path, str]):
    """
    Go through header files and implementation files and scan for `#include`
    keyword, then maybe some regex to extract the file name.
    For each file we go through, we create a list of the files required by
    it.

    With C++20 and C++23 we will have to include import statements as well
    But we leave this for future work
    
    :param file: path to C++ file in current project
    return: returns: a list of the files that `file` depends on
    """
    with open(file) as f:
        # some files may have macros that check for operatoring system or 
        # compiler compatibilities. For now we ignore these as well.
        # We also need to ignore include statements made in comments 
        include_statements = []
        b_is_block_comment = False # Lines that start with /*
        for line in f.readlines():
            if b_is_block_comment:
                if line.split()[0] == '*/':
                    b_is_block_comment = False
                else:
                    continue
            else:
                if line.contains('/*'):
                    b_is_block_comment = True
                    continue
                elif line.strip()[0:2] == '//':
                    continue
                elif line.split()[0] in ('#include', '%:include'):
                    # we always expect the included file to be given second (required
                    # by standards)
                    re_match = include_statement_pattern.match(line.split()[1])
                    # We only expect one entry in the list
                    if re_match: # first matching group is empty
                        continue
                    else:
                        if not re_match.group(1): # Check if match with `<...>` is empty
                            include_statements.append(re_match.group(2))
                        else: # since we have a match and first group is non-empty we
                              # apend
                            include_statements.append(re_match.group(1))
                    else:
                        continue
        return include_statements


def output_dependency_tree_to_dot_file(dep_tree: Dict[List[Union[Path, str]]], output_name: Optional[Union[Path, str]]):
    """
    Goes through dictionary of files gathered from recursive search of directory and prints all
    the nodes it will be attached to in file named output_name.
    Output is formated to be compatible with the DOT command line program: https://graphviz.org/doc/info/lang.html

    :param dep_tree: dictionary with files in project as keys and list of their dependencies as value
    :param output_name: name of output file or path to output file 
    """
    if not isinstance(dep_tree, dict):
        # For cleaner debugging messages, only keep while still developing program
        print("None dictionary object passed.")
        quit()

    if not output_name:
        output_name = 'includes_tree_output.dot'
    
    # TODO: Need to colorize output. 
    #       E.g. header files are blue, translation units red
    #       Standard Template Library files are different shaped bubbles, etc
    #       Of course this will require a key of some sort to be documentd somewhere
    with open(output_name) as f:
        f.write("graph {\n")
        for key, dep_list in dep_tree.items():
            for entry in dep_list:
                f.write(f"\"{key}\" -- \"{entry}\";\n")
        f.write("}")


def generate_dependency_tree(files_in_project: List[Path]):
    pass
