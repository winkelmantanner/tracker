import os
import sys
import base64

from diff import generate_diff_of_relevant_trees, relevant_subtrees, BYTES_CHAR

def load_file_contents(path_string):
    with open(path_string, 'r' + BYTES_CHAR) as bytes_generator:
        file_bytes = bytes_generator.read()
    return file_bytes

def load_one_file(tree, path_string_to_containing_folder, file_name):
    path_list = path_string_to_containing_folder.split(os.sep)
    current_position = tree
    for directory in path_list:
        if directory in current_position:
            if type(current_position[directory]) == type(dict()):
                current_position = current_position[directory]
            else:
                raise Exception("Found file already in tree where a directory was expected based on the path")
        else:
            current_position[directory] = {}
            current_position = current_position[directory]
    current_position[file_name] = load_file_contents(path_string_to_containing_folder + str(os.sep) + file_name)


def load_tree(root):
    tree = {}
    for path_string, dir_list, file_list in os.walk(root):
        for file_name in file_list:
            load_one_file(tree, path_string, file_name)
    return tree


if __name__=='__main__':
    tree_a = load_tree('.')
    for line in sys.stdin:
        tree_b = load_tree('.')
        left_diff_tree, right_diff_tree = relevant_subtrees(tree_a, tree_b)
        print(''.join(generate_diff_of_relevant_trees(left_diff_tree, right_diff_tree)))
        tree_a = tree_b