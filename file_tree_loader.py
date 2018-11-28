import os
import sys
import base64
import re
import tracker

import diff
from diff import generate_diff_of_relevant_trees, generate_context_diffs_between_dicts, relevant_subtrees, BYTES_CHAR

def load_file_contents(path_string):
    with open(path_string, 'r' + BYTES_CHAR) as bytes_generator:
        file_bytes = bytes_generator.read()
    return file_bytes

def load_one_file_into_tree(tree, path_string_to_containing_folder, file_name):
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



def load_one_file_path_into_dict(dictionary, path_string_to_containing_folder, file_name):
    path = path_string_to_containing_folder + str(os.sep) + file_name
    dictionary[path] = load_file_contents(path)

def generate_files_location_and_name(root):
    for path_string, dir_list, file_list in os.walk(root):
        # ignore trackerfiles
        if not re.match('^\.?' + os.sep + '?' + tracker.TRACKER_FOLDER_NAME, path_string):
            for file_name in file_list:
                yield path_string, file_name

def load_dict(root):
    dictionary = dict()
    for path_string, file_name in generate_files_location_and_name(root):
        load_one_file_path_into_dict(dictionary, path_string, file_name)
    return dictionary


def load_tree(root):
    tree = {}
    for path_string, file_name in generate_files_location_and_name(root):
        load_one_file_into_tree(tree, path_string, file_name)
    return tree



def current_context_diff():
    current_state_name = tracker.get_current_state_name()
    current_file_system_state = load_dict(tracker.get_trackerfiles_parent_path_or_empty_string())
    saved_file_system_state = compute_file_system_state_from_history(current_state_name)
    return ''.join(generate_context_diffs_between_dicts(saved_file_system_state, current_file_system_state))


def compute_file_system_state_from_history(state_name):
    previous_state_name, patch_dict = tracker.read_previous_state_name_and_patch_data_from_file(state_name)
    # print("compute_file_system_state_from_history was called;  PREVIOUS STATE:" + str(previous_state_name) + " PATCH_DICT:" + str(patch_dict))
    if previous_state_name == None:
        return diff.apply_dmp_patch_dict({}, patch_dict)
    else:
        if previous_state_name == state_name:
            raise Exception("Perpetual recursion prevented: state " + state_name + " had itself listed as its predecessor.")
        return diff.apply_dmp_patch_dict(compute_file_system_state_from_history(previous_state_name), patch_dict)

def save_dict(state_name, file_dict):
    old_state_name = tracker.get_current_state_name()
    try:
        tracker.read_previous_state_name_and_patch_data_from_file(state_name)
        return "state " + state_name + " already exists"
    except Exception:
        saved_filesystem_state = compute_file_system_state_from_history(old_state_name)
        # print("TANNER COMPUTED STATE FROM HISTORY:")
        # print(saved_filesystem_state)
        # print("TANNER CURRENT FILESYSTEM STATE:")
        # print(current_filesystem_state)
        patch_dict = diff.compute_dmp_patch_dict(saved_filesystem_state, file_dict)
        # print("TANNER COMPUTED PATCH DICT:")
        # print(patch_dict)
        tracker.write_patch_data_for_state(state_name, old_state_name, patch_dict)
        tracker.set_current_state_name(state_name)
        return ''


def save(new_state_name):
    current_filesystem_state = load_dict(tracker.get_trackerfiles_parent_path_or_empty_string())
    return save_dict(new_state_name, current_filesystem_state)



def delete_files_in_dict(file_dict):
    """
    raises Exceptions
    :param file_dict:
    :return:
    """
    for file_path in file_dict:
        if os.path.isfile(file_path):
            # delete the file
            os.remove(file_path)

            # delete empty containing folders
            if file_path[0] != '.':
                raise Exception("prevented deleting non-relative path " + str(file_path))
            iterating_path = file_path
            count = 0
            while iterating_path.find(os.sep) >= 0 and count < 5000:
                iterating_path, file_name = os.path.split(iterating_path)
                if os.listdir(iterating_path) == []:
                    os.rmdir(iterating_path)
            if count >= 5000:
                raise Exception("Infinite loop prevented when processing path " + str(file_path))

def create_files_in_dict(file_dict):
    for file_path in file_dict:
        containing_folder_path, file_name = os.path.split(file_path)
        my_makedirs(containing_folder_path)
        with open(file_path, 'wb') as file:
            file.write(diff.str_to_file_type(file_dict[file_path]))

def my_makedirs(path):
    if path.find(os.sep) < 0:
        return
    parent_path, child_name = os.path.split(path)
    my_makedirs(parent_path)
    if not os.path.exists(path):
        os.mkdir(path)


def main():
    root = '.'
    tree_a = load_dict(root)
    for line in sys.stdin:
        tree_b = load_dict(root)
        # left_diff_tree, right_diff_tree = relevant_subtrees(tree_a, tree_b)
        print(''.join(generate_context_diffs_between_dicts(tree_a, tree_b)))
        tree_a = tree_b

if __name__=='__main__':
    print(load_dict('.'))
    main()
