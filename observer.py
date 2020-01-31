import subprocess
from subprocess import run

# observe slice output and check correctness

oracle = ''  # the expected output of the program to the terminal
run_command = []
compilation_instructions = []


def construct_oracle(project_dir, run_command_, compilation_instructions_=[]):
    # cd into project directory
    # run compilation instructions (if there are any)
    # run main file with arguments
    # observe expected output and store in oracle

    # project dir = string run_command = string
    # compilation_instructions = list of commands to run inside project dir to compile

    global run_command
    global compilation_instructions
    run_command = run_command_
    compilation_instructions = compilation_instructions_

    for instruction in compilation_instructions:
        exit_code = run(instruction.split(' '), capture_output=True, cwd=project_dir)

    global oracle
    oracle = run(run_command.split(' '), capture_output=True, cwd=project_dir)
    print(oracle)


def observe_slice(slice_dir):
    # cd into slice dir
    # run main file (stored as global variable)
    # observe slice output
    # return whether or not slice output is the same as oracle

    global run_command
    global compilation_instructions

    for instruction in compilation_instructions:
        exit_code = run(instruction.split(' '), capture_output=True, cwd=slice_dir)

    if exit_code.returncode != 0:
        return False

    global oracle
    try:
        observation = run(run_command.split(' '), capture_output=True, cwd=slice_dir, timeout=2)
    except subprocess.TimeoutExpired:
        return False

    valid = oracle.returncode == observation.returncode
    valid = valid and oracle.stderr == observation.stderr
    valid = valid and oracle.stdout == observation.stdout
    return valid


if __name__ == "__main__":
    construct_oracle('./projects/c/ex-1/', './a.out 4 5', ['gcc main.c'])
    print(observe_slice('./projects/c/ex-1/'))
