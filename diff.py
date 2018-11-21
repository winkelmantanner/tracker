
import difflib

DELIM = '\n'

def diff(texta, textb, from_file_name, to_file_name):
    linesa = [line + DELIM for line in texta.split('\n')]
    linesb = [line + DELIM for line in textb.split('\n')]
    return ''.join(difflib.context_diff(linesa, linesb, fromfile=from_file_name, tofile=to_file_name))


def diff_trees(tree_a, tree_b):
    a_relevant_objects_tree = {}
    b_relevant_objects_tree = {}
    for key_in_tree_a, value_in_tree_a in tree_a.items():
        if key_in_tree_a in tree_b:
            if type(value_in_tree_a) == type(dict()) and type(tree_b[key_in_tree_a]) == type(dict()):
                child_a_relevant_objects_tree, child_b_relevant_objects_tree = diff_trees(value_in_tree_a, tree_b[key_in_tree_a])
                if child_a_relevant_objects_tree != {}:
                    a_relevant_objects_tree = child_a_relevant_objects_tree
                if child_b_relevant_objects_tree != {}:
                    b_relevant_objects_tree = child_b_relevant_objects_tree
            elif type(value_in_tree_a) == type(dict()):  # tree_b[key_in_tree_a] is a file
                a_relevant_objects_tree = value_in_tree_a
                b_relevant_objects_tree = tree_b[key_in_tree_a]
            elif type(tree_b[key_in_tree_a]) == type(dict()):  # value_in_tree_a is a file
                a_relevant_objects_tree = value_in_tree_a
                b_relevant_objects_tree = tree_b[key_in_tree_a]
            else:  # both value_in_tree_a and tree_b[key_in_tree_a] are files
                if value_in_tree_a != tree_b[key_in_tree_a]:
                    a_relevant_objects_tree[key_in_tree_a] = value_in_tree_a
                    b_relevant_objects_tree[key_in_tree_a] = tree_b[key_in_tree_a]
    return a_relevant_objects_tree, b_relevant_objects_tree
