# main file, run from here to run the entire program
import xml


def slice_tree(tree, observer_function):
    # tree is the tree to be sliced
    # observer function is a function that returns whether or not the slice is valid
        # which will be different for directory slices vs file slices, so we pass it in ourselves
    # consider different ways to slice the tree (in terms of node traversal order)
    pass


if __name__ == "__main__":
    # TODO add argparse stuff so we can run slice.py directory main_file arguments
    # computing a slice first involves running the main file with arguments and observing the output
    # store the expected output in an oracle (inside observer.py)
    # then do directory-level slicing, try removing subdirectories and files using the same tree-slicing
    # once we have a minimal directory, start slicing individual files
    # convert project directory to srcML directory with util file and slice file trees
    # (the order we traverse the directory with files to slice as well as the order we slice files in is something to test)
    pass
