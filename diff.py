
import difflib

DELIM = '\n'

def diff(texta, textb, from_file_name, to_file_name):
    linesa = [line + DELIM for line in texta.split('\n')]
    linesb = [line + DELIM for line in textb.split('\n')]
    return ''.join(difflib.context_diff(linesa, linesb, fromfile=from_file_name, tofile=to_file_name))