# IncludesGraph
This application that takes a C++ project and iterates through all its files and sub-directories, 
reads the header files and translation units, and creats a graph showing the include dependencies of you project.

## Options
- You can choose to exclude std header files

## Usage
It is assumed that the user is on a Linux machine (either WSL, MacOS or Linux).
There is no installing process, just edit the setup file (i.e Ubuntu => `~/.bashrc`)
and add the line
```console
alias ig='path_to_this_repo/includes_graph'
```
To run the program execute the line
```console
ig [path_to_project_dir] [output_file_name](optional)
```
To visualize the output, `dot` must be installed. 
Automation will use the return of `build_dependency_tree`(`includes_graphs`) to format and execute the visualization
```console
dot -Tsvg [output_file_name] [output_image_name.svg]
```
