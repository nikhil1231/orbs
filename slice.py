# main file, run from here to run the entire program
import sys
import xml.etree.ElementTree as ET
from argparse import ArgumentParser
import os

sliced_dir = ""
sliced_target = ""


def observer(tree):
    # x write xml file back to sliced directory
    # x convert sliced xml directory back to compilable sliced code
    #  compile sliced code
    #  execute
    #  observe
    # use observer.py to compare to oracle

    tree.write(os.path.join(sliced_dir, sliced_target))
    from srcML_util import convert_to_source
    global args
    convert_to_source(sliced_dir, sliced_target)

    from observer import observe_slice

    observation = observe_slice(sliced_dir)
    # print(observation)
    return observation


def slice_file(tree, observer_function):
    # tree is the tree to be sliced
    # observer function is a function that returns whether or not the slice is valid
    # which will be different for directory slices vs file slices, so we pass it in ourselves
    # consider different ways to slice the tree (in terms of node traversal order)

    root = tree.getroot()
    queue = [root]

    while len(queue) != 0:
        node = queue.pop(0)

        children = list(node)[:]
        for child in children:
            node.remove(child)
            if observer_function(tree):
                pass
            else:
                node.append(child)
                queue.append(child)

    tree.write(os.path.join(sliced_dir, sliced_target))
    from srcML_util import convert_to_source
    convert_to_source(sliced_dir, sliced_target)

    from observer import observe_slice

    observation = observe_slice(sliced_dir)


def slice(path, target_file):
    from srcML_util import clone_and_convert_target

    global sliced_dir, sliced_target

    sliced_dir = clone_and_convert_target(path, target_file)

    sliced_target = ".".join(target_file.split('.')[:-1]) + ".xml"

    tree = ET.parse(os.path.join(sliced_dir, sliced_target))

    slice_file(tree, observer)


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

    from observer import construct_oracle
    construct_oracle(project_dir, './a.out 4 5', ['gcc main.c'])

    # project_dir = os.path.abspath(project_dir)

    assert os.path.isdir(project_dir)

    full_target = os.path.join(project_dir, target)
    assert os.path.exists(full_target)

    slice(project_dir, target)
