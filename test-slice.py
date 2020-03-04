# script to test various slicing orderings

import slice
from slice import clone_and_convert_target, get_node_type, calc_slice_reduction, json, ET, os, sys


def test_removing_orders(path, target_file):
    # getting a list of all elements
    sliced_dir = clone_and_convert_target(path, target_file)
    sliced_target = ".".join(target_file.split('.')[:-1]) + ".xml"
    root = ET.parse(os.path.join(sliced_dir, sliced_target)).getroot()
    queue = [root]
    nodes = []
    while len(queue):
        node = queue.pop(0)
        nodes.append(node)
        queue.extend(list(node))

    # getting a list of all element types
    types = list(set(map(lambda x: get_node_type(x), nodes)))
    types = sorted(types)

    results = {}
    # un-parallelised code:
    for t in types:
        print(f'slicing with ordering {t} first')
        sys.stdout = open(os.devnull, 'w')
        slice.slice(path, target_file, [t])
        sys.stdout = sys.__stdout__  # suppressing print statements clogging up

        reduction = calc_slice_reduction(path, target_file)
        print(f'{round(reduction, 2)}% reduction in file size')
        results[t] = reduction
        with open('./results.json', 'w+') as results_file:
            results_file.write(json.dumps(results, indent=4))

    # import multiprocessing as mp
    # p = mp.Pool(mp.cpu_count() - 1)
    # results = p.starmap(slice, [(path, target_file, [t]) for t in types])
    # print(results)


if __name__ == "__main__":
    print('=' * 10 + 'test-slice.py' + '=' * 10)
    config = slice.init_slicer()
    # slice(config['project_dir'], config['target_file'], [])
    test_removing_orders(config['project_dir'], config['target_file'])
