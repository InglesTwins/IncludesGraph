"""Main file to extract dependencies to model the include graph"""

import os
import sys
from pathlib import Path

args = [arg for arg in sys.argv]
files_in_dir = [
    [file for file in Path(root).glob('*')
     if file.suffix in ('h', 'hpp', 'c', 'cpp')]
    for root in args
]
