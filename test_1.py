from pathlib import Path
import sys
import build_dependency_tree as ig

directory = Path(__file__).absolute()
sys.path.append(directory.parent.parent.__str__())

if __name__ == '__main__':
    print(directory.parent)
    extracted_files, set_o_dirs = ig.extract_files_from_directory([directory.parent])
    ig.output_dependency_tree_to_dot_file(
            ig.generate_dependency_tree(extracted_files),
            set_o_dirs,
            Path("./test_1.dot"))
