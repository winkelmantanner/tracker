import os

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
    current_position[file_name] = "FILE"

def load_tree(root):
    tree = dict()
    for root, dirs, files in os.walk("."):
        for file in files:
            load_one_file(tree, root, file)
    print(tree)

if __name__=='__main__':
    load_tree('.')