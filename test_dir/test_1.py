from pathlib import Path
import sys

directory = Path(__file__).absolute()
sys.path.append(directory.parent.parent)

import build_dependency_tree as ig

if __name__ == '__name__':
    extracted_files = ig.extract_files_from_directory()
    ig.output_dependency_tree_to_dot_file(
            ig.generate_dependency_tree(extracted_files),
            "test_1.dot")
