"""Count words and rules from a Treebank."""

from __future__ import print_function
import sys

 
class Tree:
    def __init__(self, tag, branches, _SB, _EB):
        assert len(branches) >= 1
        for b in branches:
            assert isinstance(b, (Tree, Leaf))
        self.tag = tag
        self.branches = branches
        self._SB = _SB
        self._EB = _EB

        
    def linearized_tags(self, no_pos=True):
        return ' '.join(
            [self._SB + self.tag] + \
            [b.linearized_tags(no_pos) for b in self.branches] + \
            [self._EB + self.tag])

    def words(self):
        return ' '.join([b.words() for b in self.branches])

class Leaf:
    def __init__(self, tag, word):
        self.tag = tag
        self.word = word

    def linearized_tags(self, no_pos=True) :
        if no_pos:
            return 'XX'
        else:
            return self.tag

    def words(self):
        return self.word

class Tokenizer:
    """An iterator over the tokens of a Treebank."""
    def __init__(self, input, _SB, _EB):
        self.input = input
        self.line = []
        self._SB = _SB
        self._EB = _EB

    def __next__(self):
        """Return the next token."""
        while self.line == []:
            s = self.input.readline()
            if s == '':
                raise StopIteration
            self.line = s.replace(self._SB , ' ' + self._SB + ' ').replace( self._EB, ' ' + self._EB + ' ').split()
        return self.line.pop(0)

def read_trees(input, _SB, _EB):
    """Yield trees in a file."""
    tokens = Tokenizer(input, _SB, _EB)
    while True:
        assert tokens.__next__() == _SB
        assert tokens.__next__() == _SB
        tree = read_tree(tokens, _SB, _EB)
        if tree:
            yield tree
        assert tokens.__next__() == _EB

def read_tree(tokens, _SB, _EB):
    """Read the next well-formed tree, removing empty constituents."""
    tag = tokens.__next__().split('-')[0].split('=')[0].split('|')[0]
    element = tokens.__next__()
    if element != _SB:
        assert tokens.__next__() == _EB
        return Leaf(tag, element)
    branches = []
    while element != _EB:
        assert element == _SB
        branch = read_tree(tokens, _SB, _EB)
        if branch and branch.tag:
            branches.append(branch)
        element = tokens.__next__()
    if branches:
        return Tree(tag, branches, _SB, _EB)

def writes_trees():
    args = sys.argv[1:]
    if len(args) != 2:
        print('Usage: python3 read_trees.py path/to/tree/output path/to/words/output  < treebank')
    tree_output, words_output = args
    with open(tree_output, 'w') as tree_out:
        with open(words_output, 'w') as word_out:
            for tree in read_trees(sys.stdin, '(', ')'):
#                print('END ' + tree.linearized_tags(), file=tree_out)
                print(tree.linearized_tags(), file=tree_out)
                print(tree.words(), file=word_out)

def write_trees(tree_out, word_out, data_in, _SB, _EB):

    with open(tree_out, 'w') as tree_out:
        with open(word_out, 'w') as word_out:
            for tree in read_trees(data_in, _SB, _EB):
                print(tree.linearized_tags(), file=tree_out)
                print(tree.words(), file=word_out)

if __name__ == '__main__':
    
    writes_trees()   


