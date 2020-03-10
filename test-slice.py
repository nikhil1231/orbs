import os
import multiprocessing as mp


def run_with_order(order):
    command = f'python3 slice.py -o ' + ' '.join(order) + ' --slice-only-order'
    print(command)
    os.system(command)


if __name__ == "__main__":
    types = ['if', 'else', 'function', 'comment', 'include', 'block', 'expr_stmt', 'decl_stmt']
    types = list(map(lambda x: [x], types))
    with mp.Pool(mp.cpu_count() - 1) as P:
        P.map(run_with_order, types)
