import os
import base64

def load_file_contents_base64(path_string):
    with open(path_string, 'rb') as bytes_generator:
        file_bytes = bytes_generator.read()
    return base64.b64encode(file_bytes)

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
    current_position[file_name] = load_file_contents_base64(path_string_to_containing_folder + str(os.sep) + file_name)


def load_tree(root):
    tree = dict()
    for path_string, dir_list, file_list in os.walk(root):
        for file_name in file_list:
            load_one_file(tree, path_string, file_name)
    print(tree)

if __name__=='__main__':
    load_tree('.')