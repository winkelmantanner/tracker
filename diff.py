import os

import difflib



# ensure that all relevant places are changed if we change the fact that content is stored as bytes
BYTES_CHAR = 'b'
def str_to_file_type(string):
    return bytes(string, encoding='utf-8')
def file_type_to_str(file_type_object):
    return str(file_type_object, encoding='utf-8')
FILE_OBJECT_TYPE = type(eval(BYTES_CHAR + "''"))
DELIM = eval(BYTES_CHAR + "\'\\n\'")

def context_diff(file_object_a, file_object_b, from_file_name, to_file_name):
    """

    :param texta:
    :param textb:
    :param from_file_name:
    :param to_file_name:
    :return:
        A string (type str) of diff
    """
    linesa = [file_type_to_str(line + DELIM) for line in file_object_a.split(DELIM)]
    linesb = [file_type_to_str(line + DELIM) for line in file_object_b.split(DELIM)]
    return ''.join(difflib.context_diff(linesa, linesb, fromfile=from_file_name, tofile=to_file_name))



def relevant_subtrees(tree_a, tree_b):
    """
    This function will return a subset of tree_a and a subset of tree_b, each containing only items that differ

    :param tree_a:
        The first filesystem tree.
    :param tree_b:
        The second filesystem tree.

    :return:
        Two trees.
        A subset of tree_a and a subset of tree_b, each containing only items that differ
    """
    a_relevant_objects_tree = {}
    b_relevant_objects_tree = {}
    for key in set(tree_a.keys()).union(set(tree_b.keys())):
        if key in tree_a and key in tree_b:
            if type(tree_a[key]) == type(dict()) and type(tree_b[key]) == type(dict()):
                child_a_relevant_objects_tree, child_b_relevant_objects_tree = relevant_subtrees(tree_a[key], tree_b[key])
                if child_a_relevant_objects_tree != {}:
                    a_relevant_objects_tree[key] = child_a_relevant_objects_tree
                if child_b_relevant_objects_tree != {}:
                    b_relevant_objects_tree[key] = child_b_relevant_objects_tree
            elif type(tree_a[key]) == type(dict()):  # tree_b[key] is a file
                a_relevant_objects_tree[key] = tree_a[key]
                b_relevant_objects_tree[key] = tree_b[key]
            elif type(tree_b[key]) == type(dict()):  # tree_a[key] is a file
                a_relevant_objects_tree[key] = tree_a[key]
                b_relevant_objects_tree[key] = tree_b[key]
            else:  # both tree_a[key] and tree_b[key] are files
                if tree_a[key] != tree_b[key]:
                    a_relevant_objects_tree[key] = tree_a[key]
                    b_relevant_objects_tree[key] = tree_b[key]
        elif key in tree_a:
            a_relevant_objects_tree[key] = tree_a[key]
        elif key in tree_b:
            b_relevant_objects_tree[key] = tree_b[key]
    return a_relevant_objects_tree, b_relevant_objects_tree



def generate_diff_of_relevant_trees(a_relevant_tree, b_relevant_tree, path=''):
    for key in set(a_relevant_tree.keys()).union(set(b_relevant_tree.keys())):
        path_with_key = key
        if path != '':
            path_with_key = path + str(os.sep) + key
        try:
            if key in a_relevant_tree and key in b_relevant_tree:
                if type(a_relevant_tree[key]) == FILE_OBJECT_TYPE and type(b_relevant_tree[key]) == FILE_OBJECT_TYPE:
                    yield context_diff(a_relevant_tree[key], b_relevant_tree[key], path_with_key, path_with_key)
                elif type(a_relevant_tree[key]) == FILE_OBJECT_TYPE:  # b_relevant_tree[key] is a directory
                    yield context_diff(a_relevant_tree[key], str_to_file_type(""), path_with_key, "")
                    yield ''.join(generate_diff_of_relevant_trees({}, b_relevant_tree[key], path_with_key))
                elif type(b_relevant_tree[key]) == FILE_OBJECT_TYPE:  # a_relevant_tree[key] is a directory
                    yield context_diff(str_to_file_type(""), b_relevant_tree[key], "", path_with_key)
                    yield ''.join(generate_diff_of_relevant_trees(a_relevant_tree[key], {}, path_with_key))
                else:
                    yield ''.join(generate_diff_of_relevant_trees(a_relevant_tree[key], b_relevant_tree[key], path_with_key))
            elif key in a_relevant_tree:
                if type(a_relevant_tree[key]) == FILE_OBJECT_TYPE:
                    yield context_diff(a_relevant_tree[key], str_to_file_type(""), path_with_key, "")
                else:
                    yield ''.join(generate_diff_of_relevant_trees(a_relevant_tree[key], {}, path_with_key))
            elif key in b_relevant_tree:
                if type(b_relevant_tree[key]) == FILE_OBJECT_TYPE:
                    yield context_diff(str_to_file_type(""), b_relevant_tree[key], "", path_with_key)
                else:
                    yield ''.join(generate_diff_of_relevant_trees({}, b_relevant_tree[key], path_with_key))
        except UnicodeDecodeError:
            yield file_type_to_str(DELIM) + 'Binary file ' + path_with_key + ' differs' + file_type_to_str(DELIM)
