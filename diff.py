import os
import traceback
import difflib
import diff_match_patch as dmp_module
dmp = dmp_module.diff_match_patch()


# ensure that all relevant places are changed if we change the fact that content is stored as bytes
BYTES_CHAR = 'b'
EMPTY_FILE = b''
FILE_OBJECT_TYPE = type(eval(BYTES_CHAR + "''"))
DELIM = eval(BYTES_CHAR + "\'\\n\'")

def str_to_file_type(string):
    if type(string) == type(''):
        return bytes(string, encoding='utf-8')
    else:
        return string
def file_type_to_str(file_type_object):
    if type(file_type_object) == type(EMPTY_FILE):
        return str(file_type_object, encoding='utf-8')
    else:
        return file_type_object

STR_DELIM = file_type_to_str(DELIM)


def context_diff(file_object_a, file_object_b, from_file_name, to_file_name):
    """
    DO NOT CALL.  CALL safe_context_diff INSTEAD.

    :param file_object_a:
        MUST BE TYPE BYTES
    :param file_object_b:
        MUST BE TYPE BYTES
    :param from_file_name:
        MUST BE TYPE STR
    :param to_file_name:
        MUST BE TYPE STR
    :return:
        A string (type str) of diff
    """
    splittext_a = file_type_to_str(file_object_a).split(STR_DELIM)
    splittext_b = file_type_to_str(file_object_b).split(STR_DELIM)
    linesa = [line + STR_DELIM for line in splittext_a]
    linesb = [line + STR_DELIM for line in splittext_b]
    return ''.join(difflib.context_diff(linesa, linesb, fromfile=from_file_name, tofile=to_file_name))

def safe_context_diff(file_object_a, file_object_b, from_file_name, to_file_name):

    # make sure only the right types are passed
    file_a = file_object_a
    if type(file_object_a) != type(EMPTY_FILE):
        file_a = str_to_file_type(file_object_a)
    file_b = file_object_b
    if type(file_object_b) != type(EMPTY_FILE):
        file_b = str_to_file_type(file_object_b)

    try:
        return context_diff(file_a, file_b, from_file_name, to_file_name)
    except Exception as e:
        if from_file_name != '' and to_file_name != '':
            return STR_DELIM + "Binary file " + from_file_name + " differs" + STR_DELIM + STR_DELIM
        elif from_file_name != '':
            return STR_DELIM + "Binary file " + from_file_name + " was deleted" + STR_DELIM + STR_DELIM
        elif to_file_name != '':
            return STR_DELIM + "Binary file " + to_file_name + " was created" + STR_DELIM + STR_DELIM



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
        if key in a_relevant_tree and key in b_relevant_tree:
            if type(a_relevant_tree[key]) == FILE_OBJECT_TYPE and type(b_relevant_tree[key]) == FILE_OBJECT_TYPE:
                yield safe_context_diff(a_relevant_tree[key], b_relevant_tree[key], path_with_key, path_with_key)
            elif type(a_relevant_tree[key]) == FILE_OBJECT_TYPE:  # b_relevant_tree[key] is a directory
                yield safe_context_diff(a_relevant_tree[key], str_to_file_type(""), path_with_key, "")
                yield ''.join(generate_diff_of_relevant_trees({}, b_relevant_tree[key], path_with_key))
            elif type(b_relevant_tree[key]) == FILE_OBJECT_TYPE:  # a_relevant_tree[key] is a directory
                yield safe_context_diff(str_to_file_type(""), b_relevant_tree[key], "", path_with_key)
                yield ''.join(generate_diff_of_relevant_trees(a_relevant_tree[key], {}, path_with_key))
            else:
                yield ''.join(generate_diff_of_relevant_trees(a_relevant_tree[key], b_relevant_tree[key], path_with_key))
        elif key in a_relevant_tree:
            if type(a_relevant_tree[key]) == FILE_OBJECT_TYPE:
                yield safe_context_diff(a_relevant_tree[key], str_to_file_type(""), path_with_key, "")
            else:
                yield ''.join(generate_diff_of_relevant_trees(a_relevant_tree[key], {}, path_with_key))
        elif key in b_relevant_tree:
            if type(b_relevant_tree[key]) == FILE_OBJECT_TYPE:
                yield safe_context_diff(str_to_file_type(""), b_relevant_tree[key], "", path_with_key)
            else:
                yield ''.join(generate_diff_of_relevant_trees({}, b_relevant_tree[key], path_with_key))



def compute_function_between_dicts(dict1, dict2, func):
    result = {}
    for key in set(dict1.keys()).union(set(dict2.keys())):
        if key in dict1 and key in dict2:
            if dict1[key] != dict2[key]:
                r = func(dict1[key], dict2[key], key, key)
                if r != None:
                    result[key] = r
        elif key in dict1:
            r = func(dict1[key], '', key, "")
            if r != None:
                result[key] = r
        elif key in dict2:
            r = func('', dict2[key], "", key)
            if r != None:
                result[key] = r
    return result

def compute_context_diffs_between_dicts(dict1, dict2):
    return compute_function_between_dicts(dict1, dict2, safe_context_diff)

def generate_context_diffs_between_dicts(dict1, dict2):
    diff_dict = compute_context_diffs_between_dicts(dict1, dict2)
    for key in diff_dict:
        yield diff_dict[key]


def compute_dmp_patch_between_file_objects(file1, file2, *args):
    try:
        string1 = file_type_to_str(file1)
        string2 = file_type_to_str(file2)
        patch = compute_dmp_patch_from_strings(string1, string2)
        if patch != []:
            return patch
        else:
            return None
    except Exception:
        return (file1, file2, )  # the , denontes a tuple

def compute_dmp_patch_dict(dict1, dict2):
    return compute_function_between_dicts(dict1, dict2, compute_dmp_patch_between_file_objects)

def apply_dmp_patch_with_star_args(dmp_patch, string, *args):
    return apply_dmp_patch(dmp_patch, string)

def apply_dmp_patch_dict(destination_dict, patch_dict):
    return compute_function_between_dicts(patch_dict, destination_dict, apply_dmp_patch_with_star_args)


def compute_dmp_diff(string1, string2):
    return dmp.diff_main(string1, string2)

def compute_dmp_patch_from_strings(string1, string2):
    return dmp.patch_make(string1, string2)

def apply_dmp_patch(dmp_patch, string):
    if type(dmp_patch) == type(tuple()):
        return dmp_patch[1]
    return dmp.patch_apply(dmp_patch, string)[0]



# Only used in driver below
def compute_dmp_patch_from_diff(string, diff):
    return dmp.patch_make(string, diff)

def apply_dmp_diff(string, diff):
    dmp_patch = compute_dmp_patch_from_diff(string, diff)
    return apply_dmp_patch(dmp_patch, string)

def apply_changes_dmp(destination, source, base):
    return apply_dmp_diff(destination, compute_dmp_diff(base, source))

if __name__=='__main__':
    dest = 'qwerqwerqwer'
    source = 'qaerqaer'
    base = 'asdfqwer'
    result = apply_changes_dmp(dest, source, base)
    print(result)