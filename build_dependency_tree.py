"""Main file to extract dependencies to model the include graph"""

import sys
import re
from pathlib import Path
from typing import Optional
from typing import List


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


def create_single_file_dependency_list(file: Path):
    """
    TODO: Go through header files and implementation files and scan for `#include`
          keyword, then maybe some regex to extract the file name.
          For each file we go through, we create a list of the files required by
          it.
    NOTE: With C++20 and C++23 we will have to include import statements as well
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
                elif line.split() == '//':
                    continue
                elif line.split()[0] == '#include':
                    # match either the pattern `<...>` or `"..."`
                    # re.findall will return a list of tuples `[(pattern 1, pattern 2), ...]`
                    re_match = re.findall(r"<(.+?.)>|\"(.+?.)\"", line.split()[1])[0]
                    # We only expect one entry in the list
                    if not re_match[0]: # first matching group is empty
                        continue
                    else:
                        include_statements.append(re_match[0])
                else:
                    continue
        return include_statements
