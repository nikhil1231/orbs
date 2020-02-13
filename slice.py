# main file, run from here to run the entire program
import sys
import xml.etree.ElementTree as ET
from argparse import ArgumentParser
import os
from tqdm import tqdm
import shutil

sliced_dir = ""
sliced_target = ""


def observer(tree=None):
    if tree:
        tree.write(os.path.join(sliced_dir, sliced_target))
    from srcML_util import convert_to_source
    # global args
    try:
        convert_to_source(sliced_dir, sliced_target)
    except:
        return False
    from observer import observe_slice

    observation = observe_slice(sliced_dir)
    # print(observation)
    return observation


def slice_file(tree, observer_function):
    print('performing file slice')
    # tree is the tree to be sliced
    # observer function is a function that returns whether or not the slice is valid
    # which will be different for directory slices vs file slices, so we pass it in ourselves
    # consider different ways to slice the tree (in terms of node traversal order)

    root = tree.getroot()
    queue = [root]
    total_nodes = sum(1 for _ in root.iter("*"))
    traversed_nodes = 0

    pbar = tqdm(total=total_nodes)
    # for i in tqdm(range(total_nodes)):
    while len(queue) != 0:
        node = queue.pop(0)
        traversed_nodes = 1
        children = list(node)[:]
        for child in children:
            node.remove(child)
            if observer_function(tree):
                # we removed all subelements in with the child, equivalent to traversing them
                traversed_nodes += (sum(1 for _ in child.iter("*")))
            else:
                node.append(child)
                queue.append(child)
        pbar.update(traversed_nodes)
    pbar.close()
    tree.write(os.path.join(sliced_dir, sliced_target))
    from srcML_util import convert_to_source
    convert_to_source(sliced_dir, sliced_target)

    print('slice complete, recompiling project')
    from observer import compile_project

    compile_project(sliced_dir)


def slice_directory(observer_function):
    print('performing directory-level slice')
    # walk the directory
    # make copies of things we want to delete inside a temp folder
    # delete the thing
    # observe
    # move on or copy back in the saved folder/file
    # note that the queue only contains directories, since we test file removal for each directory
    queue = [sliced_dir]
    if os.path.isdir('./temp'):
        shutil.rmtree('./temp')
    os.mkdir('./temp')

    total_files = sum([len(files) for r, d, files in os.walk(sliced_dir)])

    # pbar = tqdm(total=total_files)
    while len(queue) != 0:
        dir_path = queue.pop(0)
        if os.path.isdir(dir_path):
            traversed_files = 0
            children = os.listdir(dir_path)
            # print('d', dir_path)
            # print('c', children)
            for child in children:
                full_path = os.path.join(dir_path, child)
                # print(child, full_path)
                if os.path.isdir(full_path):
                    traversed_files = 0
                    # try removal and observe
                    # counting subdirectories that might get removed
                    subdir_count = sum([len(files) for r, d, files in os.walk(full_path)])
                    # print('sbc', child, subdir_count)
                    # saving copy of directory and removing
                    shutil.copytree(full_path, f'./temp/{child}')
                    shutil.rmtree(full_path)

                    traversed_files = subdir_count
                    observation = observer_function(False)  # replace this with real observer func
                    if observation:
                        # we can remove, dont do anything
                        pass
                    else:
                        # we are unable to remove this directory, add it back in and append it's children paths to the queu
                        shutil.move(f'./temp/{child}', full_path)
                        for subdir in os.listdir(full_path):
                            queue.append(os.path.join(full_path, subdir))
                else:
                    # remove file and observe
                    traversed_files = 1
                    shutil.copy(full_path, f'./temp/{child}')
                    os.remove(full_path)

                    observation = observer_function(False)  # replace this with real observer func
                    if observation:
                        # we can remove, dont do anything
                        pass
                    else:
                        # we are unable to remove this file, add it back
                        shutil.move(f'./temp/{child}', full_path)
    #         print(traversed_files)
    #         pbar.update(traversed_files)
    # pbar.close()

    shutil.rmtree('./temp')
    pass


def slice(path, target_file):
    from srcML_util import clone_and_convert_target

    global sliced_dir, sliced_target
    print('creating cloned xml-ified project')
    sliced_dir = clone_and_convert_target(path, target_file)

    sliced_target = ".".join(target_file.split('.')[:-1]) + ".xml"

    tree = ET.parse(os.path.join(sliced_dir, sliced_target))
    print('beginning slice...')
    slice_directory(observer)
    slice_file(tree, observer)

    # TODO instead of just counting main file lines, also test total filesize of the project

    original_file_length = len(open(os.path.join(path, target_file), 'r').readlines())
    sliced_file_length = len(open(os.path.join(sliced_dir, sliced_target), 'r').readlines())

    print(f'original file length: {original_file_length}')
    print(f'sliced file length: {sliced_file_length}')

    print(f'{round((original_file_length - sliced_file_length) / original_file_length * 100.0, 2)}% reduction in file size')


if __name__ == "__main__":
    # TODO add argparse stuff so we can run slice.py directory main_file arguments
    # computing a slice first involves running the main file with arguments and observing the output
    # store the expected output in an oracle (inside observer.py)
    # then do directory-level slicing, try removing subdirectories and files using the same tree-slicing
    # once we have a minimal directory, start slicing individual files
    # convert project directory to srcML directory with util file and slice file trees
    # (the order we traverse the directory with files to slice as well as the order we slice files in is something to test)

    '''Usage: python slice.py <directory> <target_file>

    Currently only works on single files
    '''

    parser = ArgumentParser()
    parser.add_argument('project_directory', help='The project directory to be sliced.')
    parser.add_argument('target_file_path', help='The path of the target file to be sliced. Path must be relative to the project directory.')

    args = parser.parse_args()
    project_dir = args.project_directory
    target = args.target_file_path

    print('=' * 10 + 'slice.py' + '=' * 10)

    from observer import construct_oracle
    construct_oracle(project_dir, './a.out 4 5', ['gcc main.c'])

    # project_dir = os.path.abspath(project_dir)

    assert os.path.isdir(project_dir)

    full_target = os.path.join(project_dir, target)
    assert os.path.exists(full_target)

    slice(project_dir, target)
