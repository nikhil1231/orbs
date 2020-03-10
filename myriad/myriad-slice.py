import sys
import os
repo_path = '/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-1])
sys.path.append(repo_path)

from slice import init_slicer, slice, calc_slice_reduction

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--order', nargs='+', help='<optional> node traversal ordering', required=False)
    parser.add_argument('--slice-all-nodes', help='<optional> flag, whether to slice all xml nodes or just the ones related to code blocks', action='store_true')
    parser.add_argument('--slice-only-order', help='<optional> flag, whether to slice just the nodes listed in -o order', action='store_true')
    args = parser.parse_args()
    if args.order is None:
        args.order = []
    print('=' * 10 + 'slice.py' + '=' * 10)
    print(args)
    config = init_slicer('~/Scratch/work-dir/myriad/config.json')
    # TODO add directory as an order option
    slice(config['project_dir'], config['target_file'], args.order)
    print(calc_slice_reduction(config['project_dir'], config['target_file']))
