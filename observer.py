# observe slice output and check correctness

oracle = ''  # the expected output of the program to the terminal
main_file = ''
args = []


def construct_oracle(project_dir, main_file_, args_):
    # cd into project directory
    # run main file with arguments
    # observe expected output and store in oracle
    # project dir = string main_file = string, args = list
    main_file = main_file_
    args = args_
    pass


def observe_slice(slice_dir):
    # cd into slice dir
    # run main file (stored as global variable)
    # observe slice output
    # return whether or not slice output is the same as oracle
    return True
