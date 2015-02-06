# docstringr.py
#
# felix effenberger, feb 2015
#
# generates numpy style docstrings for python source
# code


from lib2to3.pytree import Leaf, Node
from symbol import *
import sys
from lib2to3.pgen2 import driver
from lib2to3 import pygram, pytree
import re

# adjust to need
PADDING_SPACES = 4


class DocstringBuilder(object):
    def __init__(self, padding):
        object.__init__(self)
        self.leaves = []
        self.padding = padding

    def append_newline(self):
        self.leaves.append(Leaf(4, '\n'))

    def append_padding(self):
        self.leaves.append(Leaf(5, self.padding))

    def append_padded_newline(self):
        self.append_newline()
        self.append_padding()

    def append_string(self, string):
        self.leaves.append(Leaf(3, string))
        self.append_newline()
        self.append_padding()

    def append_multiline_string(self, string):
        lines = string.split('\n')
        for line in lines:
            line_padding = line.replace('\t', ' ' * PADDING_SPACES).replace('\n', '')
            self.append_string(line_padding)

    def insert_into_tree(self, tree, position=0):
        print "inserting"
        print self.leaves
        print '--'
        docstring_node = Node(313, self.leaves)  # simple_stmt
        tree.children.insert(position, docstring_node)

    def flush(self):
        self.leaves = []


def walk_class(tree):
    # TODO implement class walker (for class docstrings)
    pass


def walk_func(tree):
    # function subtree
    func = tree.children
    func_name = func[1].value
    func_args = None
    # search for arguments
    for fa in func[2].children:
        if fa.type == 334:
            func_args = fa
            break

    # extract arguments
    args = []
    if func_args is not None:
        func_args = func_args.children
        i = 0
        while i < len(func_args):
            if func_args[i].type == 1:
                arg = [func_args[i].value]
                if i < len(func_args) - 2 and func_args[i + 1].type == 22:
                    if isinstance(func_args[i + 2], Leaf):
                        # atom
                        arg.append(func_args[i + 2].value)
                    else:
                        # compound
                        arg.append(str(func_args[i + 2]))
                    i += 3
                else:
                    i += 2
                args.append(arg)
            else:
                i += 1

    # search for body
    body = None
    for fa in func:
        if fa.type == 321:  # suite
            body = fa
            break

    # collect padding
    padding = ''
    first = -1
    for i, b in enumerate(body.children):
        if b.type < 255:
            if b.type == 5:  # padding
                padding += b.value
            first = i
        else:
            break

    docstring = DocstringBuilder(padding)
    docstring.append_padded_newline()
    docstring.append_multiline_string('"""\nMissing documentation')

    if len(args) > 0:
        if not (len(args) == 1 and (args[0][0] == 'self' or args[0][0] == 'cls')):
            docstring.append_padded_newline()
            docstring.append_multiline_string('Parameters\n----------')

            # function arguments
            for arg in args:
                if arg[0] == 'self' or arg[0] == 'cls':
                    continue
                p_def = ''
                pd = None
                if len(arg) == 2:
                    pd = arg[1]
                    p_def = ' (default %s)' % arg[1]

                t = 'Type'
                if pd:
                    # type guessing
                    if pd == 'True' or pd == 'False':
                        t = 'bool'
                    if (pd[0] == "'" or pd[0] == '"') and pd[-1] == pd[0]:
                        t = 'str'
                    if re.match(r'[+\-0-9]+', pd):
                        t = 'int'
                    elif re.match(r'[+\-0-9e\.]+', pd):
                        t = 'float'

                p = '%s : %s' % (arg[0], t)
                if len(arg) == 2:
                    p += ', optional'

                docstring.append_multiline_string(
                    p + '\n' + (' ' * PADDING_SPACES) + 'Description' + p_def)

    docstring.append_padded_newline()
    docstring.append_multiline_string(
        'Returns\n-------\nValue : Type\n' + (' ' * PADDING_SPACES) + 'Description')
    docstring.append_string('""""')
    docstring.insert_into_tree(body)
    docstring.flush()


# AST nodes
# 313 - existing docstring
# 292 - funcdef
# 266 - class definion
# 321 - suite (class, function content)

def walk_tree(tree):
    for child in tree.children:
        if child.type == 266:  # classdef
            walk_tree(child)
            walk_class(child)
        if child.type == 274:  # decorated
            walk_tree(child)
        if child.type == 321:  # suite
            walk_tree(child)
        if child.type == 292:  # funcdef
            walk_func(child)


def main():
    import glob
    import os

    if len(sys.argv) != 2:
        print "usage docstringr.py PATH_TO_PYTHON_FILES"
        sys.exit(1)

    path = sys.argv[1]
    for fn in glob.glob(os.path.join(path, '*.py')):
        print 'processing %s' % fn
        print 'reading...'
        with open(fn, 'r') as f:
            contents = f.read()

        print 'parsing...'
        drv = driver.Driver(pygram.python_grammar, pytree.convert)
        tree = drv.parse_string(contents, True)
        walk_tree(tree)

        out_file = fn + '_docstringed'
        print 'writing {} ...'.format(out_file)
        with open(out_file, 'w') as f:
            f.write(str(tree))

    print 'all done'


if __name__ == "__main__":
    main()
