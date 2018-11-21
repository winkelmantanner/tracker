
import difflib

DELIM = '\n'

def diff(texta, textb, from_file_name, to_file_name):
    linesa = [line + DELIM for line in texta.split('\n')]
    linesb = [line + DELIM for line in textb.split('\n')]
    return ''.join(difflib.context_diff(linesa, linesb, fromfile=from_file_name, tofile=to_file_name))


def diff_trees(tree_a, tree_b):
    a_relevant_objects_tree = {}
    b_relevant_objects_tree = {}
    for key in set(tree_a.keys()).union(set(tree_b.keys())):
        if key in tree_a and key in tree_b:
            if type(tree_a[key]) == type(dict()) and type(tree_b[key]) == type(dict()):
                child_a_relevant_objects_tree, child_b_relevant_objects_tree = diff_trees(tree_a[key], tree_b[key])
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
