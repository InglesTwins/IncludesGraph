from pathlib import Path
import sys

directory = Path(__file__).absolute()
sys.path.append(directory.parent.parent.__str__())

import build_dependency_tree as ig

if __name__ == '__main__':
    print(directory.parent)
    extracted_files = ig.extract_files_from_directory([directory.parent])
    ig.output_dependency_tree_to_dot_file(
            ig.generate_dependency_tree(extracted_files),
            Path("./test_1.dot"))
