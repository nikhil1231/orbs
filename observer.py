import subprocess
from subprocess import run
import time
import numpy as np
from scipy.stats import norm

# observe slice output and check correctness

oracle = ''  # the expected output of the program to the terminal
run_command = []
compilation_instructions = []
compilation_time_distribution = (0, 1)  # mean, variance
execution_time_distribution = (0, 1)

use_shell = False


def compile_project(project_dir):
    global compilation_instructions
    for instruction in compilation_instructions:
        exit_code = run(instruction.split(' '), capture_output=True, cwd=project_dir, shell=use_shell)


def construct_oracle(project_dir, run_command_, compilation_instructions_=[], initialisation_samples=10):
    # cd into project directory
    # run compilation instructions (if there are any)
    # run main file with arguments
    # observe expected output and store in oracle

    # project dir = string run_command = string
    # compilation_instructions = list of commands to run inside project dir to compile
    # initialisation_samples = number of samples of how long it takes to compile/run original script
    print('constructing oracle...')
    global run_command
    global compilation_instructions
    run_command = run_command_
    compilation_instructions = compilation_instructions_

    assert initialisation_samples >= 1

    print(f'timing {initialisation_samples} compilations')
    compilation_times = []
    global compilation_time_distribution
    for i in range(initialisation_samples):
        start = time.time_ns()
        compile_project(project_dir)
        delta = time.time_ns() - start
        compilation_times.append(delta / 1000000000)
    compilation_times = np.array(compilation_times)
    compilation_time_distribution = norm.fit(compilation_times)
    print(f'compilation distributed with mean: {compilation_time_distribution[0]} std: {compilation_time_distribution[1]}')

    print(f'attempting {initialisation_samples} executions')
    global oracle
    global execution_time_distribution
    execution_times = []
    for i in range(initialisation_samples):
        start = time.time_ns()
        oracle = run(run_command.split(' '), capture_output=True, cwd=project_dir, shell=use_shell)
        delta = time.time_ns() - start
        execution_times.append(delta / 1000000000)
    execution_time_distribution = norm.fit(execution_times)
    print(f'execution distributed with mean: {execution_time_distribution[0]} std: {execution_time_distribution[1]}')

    print(f'oracle output: {oracle}')


def observe_slice(slice_dir):
    # cd into slice dir
    # run main file (stored as global variable)
    # observe slice output
    # return whether or not slice output is the same as oracle

    global run_command
    global compilation_instructions
    global execution_time_distribution
    global compilation_time_distribution

    for instruction in compilation_instructions:
        try:
            exit_code = run(instruction.split(' '), capture_output=True, cwd=slice_dir, shell=use_shell)
        except:
            return False
        if exit_code.returncode != 0:
            return False

    timeout_threshold = 1.96 * execution_time_distribution[1] + execution_time_distribution[0]
    try:
        observation = run(run_command.split(' '), capture_output=True, cwd=slice_dir, timeout=timeout_threshold, shell=use_shell)
    except:
        return False

    global oracle
    valid = oracle.returncode == observation.returncode
    valid = valid and oracle.stderr == observation.stderr
    valid = valid and oracle.stdout == observation.stdout
    return valid


if __name__ == "__main__":
    pass
    # construct_oracle('./projects/c/ex-1/', './a.out 4 5', ['gcc main.c'])
    # print(observe_slice('./projects/c/ex-1/'))
