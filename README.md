# IncludesGraph
This is a simple application that takes you project and iterates through all its subdirectories, 
reads the header files and creats a graph showing the include dependencies of you project.

## Options
- You can choose to exclude std header files

## Usage
We will assume that the user is on a Linux machine (either WSL, MacOS or Linux).
There is no installing process, this edit you setup file (for Ubuntu this `~/.bashrc`)
and add the line
```console
alias ig='path_to_this_repo/includes_graph'
```
To run the program execute the line
```console
ig [path_to_project_dir] [output_file_name](optional)
```
To visualize the output, you should have `dot` install, after `includes_graphs` has completed
simply run the command
```console
dot -Tsvg [output_file_name] [output_image_name.svg]
```
