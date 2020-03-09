# main file, run from here to run the entire program
import sys
import xml.etree.ElementTree as ET
from argparse import ArgumentParser
import os
from tqdm import tqdm
import shutil
from srcML_util import clone_and_convert_target
import json


sliced_dir = ""
sliced_target = ""


def observer(tree=None):
    if tree is not None:
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


def slice_file(tree, observer_function, ordering=[]):
    print('performing file slice')
    print(ordering)
    # tree is the tree to be sliced
    # observer function is a function that returns whether or not the slice is valid
    # consider different ways to slice the tree (in terms of node traversal order)
    tree_changed = True
    passes = 0
    while tree_changed:
        passes += 1
        tree_changed = False
        root = tree.getroot()
        queue = [root]
        ordered_nodes = []
        while len(queue) != 0:
            node = queue.pop(0)
            children = list(node)[:]
            for child in children:
                ordered_nodes.append((node, child))
                queue.append(child)

        ordered_nodes = sorted(ordered_nodes, key=lambda x: sort_nodes_by_type(x, ordering))

        slice_progress_bar = tqdm(total=len(ordered_nodes))

        while len(ordered_nodes):
            parent, child = ordered_nodes.pop(0)
            child_index = list(parent).index(child)
            parent.remove(child)
            slice_progress_bar.update(1)
            if observer_function(tree):
                tree_changed = True

                # removing all subelements from search list
                parents_to_remove = set([child])
                while len(parents_to_remove):
                    removal_parent = parents_to_remove.pop()
                    new_parents = set(list(map(lambda x: x[1], filter(lambda x: x[0] == removal_parent, ordered_nodes))))
                    slice_progress_bar.update(len(new_parents))
                    parents_to_remove = parents_to_remove.union(new_parents)
                    ordered_nodes = list(filter(lambda x: x[0] != removal_parent, ordered_nodes))
            else:
                parent.insert(child_index, child)
        slice_progress_bar.close()
        tree.write(os.path.join(sliced_dir, sliced_target))
    from srcML_util import convert_to_source
    convert_to_source(sliced_dir, sliced_target)

    print(f'file slice complete in {passes} passes, recompiling project')
    from observer import compile_project

    compile_project(sliced_dir)


def get_node_type(node):
    node_type = node.tag
    node_type = node_type[len('[http://www.srcML.org/srcML/src]'):]
    return node_type


def sort_nodes_by_type(node_pair, ordering=[]):
    node_type = get_node_type(node_pair[1])
    # sorting will order the elements like this list
    # unlisted elements will be left unordered
    if node_type in ordering:
        return ordering.index(node_type)
    return len(ordering)


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
                    observation = observer_function()  # replace this with real observer func
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

                    observation = observer_function()  # replace this with real observer func
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


def calc_slice_reduction(path, target_file):
    original_file_length = len(open(os.path.join(path, target_file), 'r').readlines())
    sliced_file_length = len(open(os.path.join(sliced_dir, sliced_target), 'r').readlines())
    return (original_file_length - sliced_file_length) / original_file_length * 100.0


def slice(path, target_file, order, should_slice_directory=True):

    global sliced_dir, sliced_target
    print('creating cloned xml-ified project')
    sliced_dir = clone_and_convert_target(path, target_file)
    sliced_target = ".".join(target_file.split('.')[:-1]) + ".xml"
    tree = ET.parse(os.path.join(sliced_dir, sliced_target))

    print('beginning slice...')

    import sys
    if should_slice_directory:
        slice_directory(observer)
    slice_file(tree, observer, order)
    # TODO instead of just counting main file lines, also test total filesize of the project


def init_slicer():
    "loads config file, constructs oracle and returns config file"
    import json
    with open('./config.json', 'r') as config_file:
        config = json.load(config_file)
    print(config)

    from observer import construct_oracle
    construct_oracle(config['project_dir'], config['run_command'], config['compilation_instructions'])

    assert os.path.isdir(config['project_dir'])

    full_target = os.path.join(config['project_dir'], config['target_file'])
    assert os.path.exists(full_target)
    return config


if __name__ == "__main__":
    # computing a slice first involves running the main file with arguments and observing the output
    # store the expected output in an oracle (inside observer.py)
    # then do directory-level slicing, try removing subdirectories and files using the same tree-slicing
    # once we have a minimal directory, start slicing individual files
    # convert project directory to srcML directory with util file and slice file trees
    # (the order we traverse the directory with files to slice as well as the order we slice files in is something to test)
    print('=' * 10 + 'slice.py' + '=' * 10)
    config = init_slicer()
    slice(config['project_dir'], config['target_file'], [])
