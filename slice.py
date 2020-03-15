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
        print('converting to source failed')
        return False
    from observer import observe_slice

    observation = observe_slice(sliced_dir)
    # print(observation)
    return observation


def slice_file(tree, observer_function, ordering=[]):
    print('performing file slice')
    print(ordering)
    global args
    # tree is the tree to be sliced
    # observer function is a function that returns whether or not the slice is valid
    # consider different ways to slice the tree (in terms of node traversal order)
    tree_changed = True
    operation_count = 0
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
        if not args.slice_all_nodes:
            # TODO also add mode to ONLY slice out elements listed in ordering
            code_node_types = ['if_stmt', 'if', 'else', 'elseif', 'while', 'enum', 'function', 'comment', 'include', 'block', 'expr_stmt', 'decl_stmt']
            ordered_nodes = list(filter(lambda x: get_node_type(x[1]) in code_node_types, ordered_nodes))
        if args.slice_only_order:
            ordered_nodes = list(filter(lambda x: get_node_type(x[1]) in ordering, ordered_nodes))
        # print(list(map(lambda x: get_node_type(x[1]), ordered_nodes)))
        slice_progress_bar = tqdm(total=len(ordered_nodes))

        while len(ordered_nodes):
            parent, child = ordered_nodes.pop(0)
            child_index = list(parent).index(child)
            parent.remove(child)
            operation_count += 1
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

    print(f'file slice complete in {operation_count} operations and {passes} passes, recompiling project')
    from observer import compile_project

    compile_project(sliced_dir)
    return operation_count


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

    slice_operations = 0
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
                    slice_operations += 1
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
    return slice_operations


def calc_slice_reduction(path, target_file):
    original_file_length = len(open(os.path.join(path, target_file), 'r').readlines())
    sliced_file_length = len(open(os.path.join(sliced_dir, target_file), 'r').readlines())
    file_reduction = (original_file_length - sliced_file_length) / original_file_length * 100.0

    def get_size(start_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        return total_size

    original_folder_size = get_size(path)
    sliced_folder_size = get_size(sliced_dir)
    dir_reduction = (original_folder_size - sliced_folder_size) / original_folder_size * 100.0

    return file_reduction, dir_reduction


def slice(path, target_file, order):

    global sliced_dir, sliced_target
    print('creating cloned xml-ified project')
    sliced_dir = clone_and_convert_target(path, target_file)
    sliced_target = ".".join(target_file.split('.')[:-1]) + ".xml"
    tree = ET.parse(os.path.join(sliced_dir, sliced_target))

    print('beginning slice...')

    import sys
    dir_slice_operation_count = 0
    if args.slice_directory:
        dir_slice_operation_count = slice_directory(observer)
    file_slice_operation_count = slice_file(tree, observer, order)

    return file_slice_operation_count, dir_slice_operation_count


def init_slicer(config_path='./config.json'):
    "loads config file, constructs oracle and returns config file"
    import json
    with open(config_path, 'r') as config_file:
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

    import argparse
    parser = ArgumentParser()
    parser.add_argument('-o', '--order', nargs='+', help='<optional> node traversal ordering', required=False)
    parser.add_argument('--slice-all-nodes', help='<optional> flag, whether to slice all xml nodes or just the ones related to code blocks', action='store_true')
    parser.add_argument('--slice-only-order', help='<optional> flag, whether to slice just the nodes listed in -o order', action='store_true')
    parser.add_argument('--slice-directory', help='<optional> flag, whether to slice directory', action='store_true')
    args = parser.parse_args()
    if args.order is None:
        args.order = []
    print('=' * 10 + 'slice.py' + '=' * 10)
    print(args)
    config = init_slicer()
    # TODO add directory as an order option
    file_slice_operation_count, dir_slice_operation_count = slice(config['project_dir'], config['target_file'], args.order)
    file_reduction_percent, dir_reduction_percent = calc_slice_reduction(config['project_dir'], config['target_file'])
    results = {"file_slice_operation_count": file_slice_operation_count, "file_reduction_percent": file_reduction_percent,
               "dir_slice_operation_count": dir_slice_operation_count, "dir_reduction_percent": dir_reduction_percent}
    results['cli'] = sys.argv
    print(f'{file_reduction_percent}% reduction in main filesize with {file_slice_operation_count} slice operations')
    # renaming and saving a copy of the sliced directory
    archive_name = f'{config["project_dir"]}'
    i = 0
    while os.path.isdir(f'{archive_name}_{i}_archived'):
        i += 1
    archive_name = f'{archive_name}_{i}_archived'
    shutil.move(sliced_dir, archive_name)
    with open(archive_name + '/config.json', 'w+') as config_file:
        config_file.write(json.dumps(config, indent=4))

    with open(archive_name + '/results.json', 'w+') as results_file:
        results_file.write(json.dumps(results, indent=4))
