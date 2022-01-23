"""Main file to extract dependencies to model the include graph"""

import sys
from pathlib import Path
from typing import List

args = [arg for arg in sys.argv]
files_in_dir = [
    [file for file in Path(root).glob('*') # TODO: Make recursive search 
     if file.suffix in ('h', 'hpp', 'c', 'cpp')]
    for root in args
]

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


