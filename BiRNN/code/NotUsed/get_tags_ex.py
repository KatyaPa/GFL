from treelib import Node, Tree
import re


""" Not used """
def binarize_subtree(tree, top, max_id):
    
    children= map(lambda child: (child.identifier, child.tag) , tree.children(top)) 
    
    parent = tree.parent(top).identifier if tree.parent(top) != None else None

    #Subtree already binary
    if (len(children) <= 2):
        return (parent, max_id)

    pnode = top
    while children:

        lsubtree = tree.subtree(children[0][0])
        tree.remove_subtree(children[0][0])
        tree.paste(pnode, lsubtree)
        
        if len(children) > 2:
            rnode_tag   = "_".join(list(zip(*children[1:])[1]))
            rnode = Node(rnode_tag, max_id)
            tree.add_node(rnode, parent = pnode)
            
            max_id     += 1
            pnode       = rnode.identifier
            children    = children[1:]
            
        else:

            rsubtree = tree.subtree(children[1][0])
            tree.remove_subtree(children[1][0])
            tree.paste(pnode, rsubtree)
            children = []

    return (parent, max_id)


def binarize_tree(tree, top, max_id):

    #Subtree already binary
    if len(tree.leaves(top)) <= 2 :
        parent = tree.parent(top).identifier if tree.parent(top)!= None else None
        return (parent, max_id)
    
    for child in tree.children(top):
        top, max_id = binarize_tree(tree, child.identifier, max_id)
           
    top, max_id = binarize_subtree(tree, top, max_id)
    return (top, max_id)



def get_suptag_topdown(tree, nid, backbone, stags):

    #Stop condition
    #if we reach leaves
    if tree[nid].is_leaf():
        stags[nid] = stags[tree.parent(nid).identifier]
        return
    #if already visited this node
    elif stags.has_key(nid):
        return
    
    node_tag = tree[nid].tag 
    
    if backbone:
        if tree.siblings(nid): 
            node_tag = "\\".join([node_tag, tree.siblings(nid)[0].tag])
        pnode_tag   = stags[tree.parent(nid).identifier]
        node_tag    = "+".join([pnode_tag, node_tag])

    stags[nid] = node_tag       

   #binary tree then at most 2 children
    children = zip(map(lambda child: child.identifier, tree.children(nid)),\
            [True, False])
    
    for child in children:
        get_suptag_topdown(tree, child[0], child[1],  stags)

""" Not used """



def is_balanced(string):
    iparens = iter('(){}[]<>')
    parens  = dict(zip(iparens, iparens))
    closing = parens.values()
    stack   = []
    for ch in string:
        delim = parens.get(ch, None)
        if delim:
            stack.append(delim)
        elif ch in closing:
            if not stack or ch != stack.pop():
                return False
    return not stack

def read_balanced_line(fin):
    s = ""
    lines = iter(open(fin, 'r'))
    for line in lines:
        if line.strip():
            s = s + line.split('\n')[0]
            if (is_balanced(s) and s != ""):
                yield s
                s = ""


def get_tree(tree, line, max_id = 0, leaf_id = 1,  parent_id = None):
    
    # starts by ['(', 'pos']
    pos_tag     = line[1].split('-')[0].split('=')[0].split('|')[0]
    if  parent_id == None:
        pos_id = 0
    else:
        pos_id = max_id
        max_id      += 1

    tree.create_node(pos_tag, pos_id, parent = parent_id, data = nRange(0,0))  
    
    parent_id   = pos_id
    total_offset = 2
    

    if (line[2] != '('): 
        # sub-tree is leaf
        # line[0:3] = ['(', 'pos', 'word', ')']        
        word_tag    = line[2]
        tree.create_node(word_tag, leaf_id, parent = parent_id, data = nRange(0,0))

        return (4, max_id,  leaf_id+1)
    
    line     = line[2:]
    
    while (line[0] != ')'):
        offset, max_id, leaf_id      = get_tree(tree, line, max_id, leaf_id, parent_id)
        total_offset       += offset
        line                = line[offset:]   
    
    return (total_offset + 1, max_id, leaf_id)


def get_trees(line):
    
    tree = Tree()
    max_id =  len([w for w in re.compile('[\S]+\)').findall(line) if not w.endswith('))')]) + 1
    line = line.replace('(' , ' ( ').replace(')', ' ) ').split()[1:]
    get_tree(tree, line, max_id)
    return tree
    

class nRange(object):

    def __init__(self, minRange, maxRange):
        self.mRange = (minRange, maxRange)



def genRange(tree, nid, minR, maxR):

    if tree[nid].is_leaf():
        tree[nid].data.mRange = (minR, maxR)
        return (maxR, maxR + 1)


    for child in tree.children(nid):
        cid = child.identifier
        (minR, maxR) = genRange(tree, cid, minR, maxR)

    tree[nid].data.mRange = (min(map(lambda child: child.data.mRange[0], tree.children(nid))), \
                                max(map(lambda child: child.data.mRange[1], tree.children(nid))))

    return (minR, maxR)


def extend_path(tree, pid, leaf_id, path_dict):
 
    path_tag    = tree.parent(pid).tag
    if tree.siblings(pid): 
        siblings    = map(lambda sibling: sibling.tag ,  tree.siblings(pid))
        siblings.insert(0, path_tag)
        path_tag    = "\\".join(siblings)
    
    path_dict[leaf_id]  = "+".join([path_tag, path_dict[leaf_id]])


def gen_suptag(tree, nid, hieght_dict, path_dict):

    #Stop condition
    if tree[nid].is_leaf():
       
        pid             = tree.parent(nid).identifier
        path_dict[nid]  = tree[pid].tag

        if hieght_dict[nid] > 1 :
            extend_path(tree, pid, nid, path_dict)
                                
        return (nid, hieght_dict[nid]-1)
    
    #Recursion
    for child in tree.children(nid):
        cid = child.identifier
        (leaf_id, hieght) = gen_suptag(tree, cid, hieght_dict, path_dict)

    if (hieght == 1):
        return (None, 1) 

    elif (hieght > 1):
        pid = tree.parent(nid).identifier        
        extend_path(tree, pid, leaf_id, path_dict)
     
    return (leaf_id, hieght - 1)
      

def gen_height_list(tree, tree_dep_dict):

    hieght_dict = {}

    for leaf in  tree.leaves(tree.root):
        lid = leaf.identifier
        depid = tree_dep_dict[lid]
        if (depid == tree.root):
             hieght_dict[lid] =  tree.depth(leaf)

        else:
            minR = min(tree[depid].data.mRange[0], tree[lid].data.mRange[0])
            maxR = max(tree[depid].data.mRange[1], tree[lid].data.mRange[1])
            height = 0
            pid = tree.parent(lid).identifier
        
            while tree[pid].data.mRange[0] > minR or tree[pid].data.mRange[1] < maxR:
                height += 1             
                pid = tree.parent(pid).identifier

            hieght_dict[lid] = height

    return hieght_dict


def gen_tree_dep_dict(fin):
    
    dep_dict_list = []
    dep_dict = {}
    lines = iter(open(fin, 'r'))
    for line in lines:
        words =  line.split()
        if words :
            dep_dict[int(words[0])] = int(words[6])
        else:
            dep_dict_list.append(dep_dict)
            dep_dict = {}

    return dep_dict_list
 
def toy_demo():
    
    tree_dict_list = []

    tree_dict_list.append({None : 'A' , 'A' : ['B', 'C'], 'B': 'D', 'C':'E',\
                            'E': ['F','G'],\
                            'D' : '1', 'F' : '2', 'G':'3'})

    tree_dict_list.append({None : 'A' , 'A' : ['B', 'C'], 'B':['D','E'],\
                            'C' : '1', 'D' : '2', 'E':'3'})
    
    tree_dict_list.append({None : 'A' , 'A' : ['B','C', 'D','E'],\
                            'B' : '1', 'C' : '2', 'D' : '3', 'E' : '4'})


    tree_dict_list.append({None : 'A' , 'A' : ['B','C', 'D'], \
                            'B' : ['E', 'F', 'G'], 'C' : ['H', 'I'],\
                            'D' : ['J', 'K', 'L', 'M'], 'E' : ['N', 'O'], \
                            'N' : '1', 'O': '2', 'F': '3', 'G': '4', 'H': '5',\
                            'I': '6', 'J' :'7', 'K': '8', 'L': '9', 'M': '0'})

    tree_dict_list.append({None : 'A' , 'A' : 'B', 'B' : ['C', 'D', 'E'],\
                            'C' : ['H', 'I'], 'D' : ['J', 'K', 'L', 'M'], \
                            'E' : ['N', 'O']})


    for tree_dict in tree_dict_list[0:1]:
        tree = Tree()
        idx = 0
        ids = {None : None}
        for parents ,children in sorted(tree_dict.items()):
            for child in children: 
                ids[child] = idx 
                tree.create_node(child, idx, parent = ids[parents], data = nRange(0,0))
                idx += 1 

        tree.show(idhidden = False)
        genRange(tree, tree.root, 0, 1)
        tree.show(data_property="mRange")

        tree_dep_dict = {ids['1'] : ids['A'], ids['2'] : ids['3'], ids['3'] : ids['1'] }
        hieght_dict =  gen_height_list(tree, tree_dep_dict)
        print hieght_dict

            #hieght_dict = {ids['1']: 3, ids['2'] : 3, ids['3']: 1 }
#        hieght_dict = {ids['1']: 1, ids['2'] : 1, ids['3']: 1, ids['4']: 2 }
#        hieght_dict = { ids['1'] : 1, ids['2'] : 3, ids['3']: 1, ids['4']: 1, \
#                        ids['5'] : 3, ids['6'] : 1, ids['7']: 1, ids['8']: 2, \
#                        ids['9'] : 1, ids['0'] : 1 }
        path_dict    = {}
        gen_suptag(tree, tree.root, hieght_dict, path_dict)
        print sorted([(tree[k].tag, v) for k,v in path_dict.items()])


#def covert_ids()
#        leaf_ids = sorted(map(lambda leaf: leaf.identifier , tree.leaves(tree.root)))
#        print leaf_ids
       #        dep_dict = {}
#        for key,value in tree_dep_dict[i].items():
#            if value == 0:
#                dep_dict[leaf_ids[key - 1]] = tree.root
#            else:
#                dep_dict[leaf_ids[key - 1]] = leaf_ids[value - 1]
#        print dep_dict

def wsj_demo():
    
    fin = 'raw_data/wsj/00/wsj_0001.mrg'
    tree_dep_dict = gen_tree_dep_dict("dep_treebank")

    for i,s in enumerate(read_balanced_line(fin)):
        tree = get_trees(s)
        tree.show(idhidden = False)
        genRange(tree, tree.root, 0, 1)
        tree.show( idhidden = False, data_property="mRange")

        print tree_dep_dict[i]

        hieght_dict =  gen_height_list(tree, tree_dep_dict[i])
        print hieght_dict
        path_dict    = {}
        gen_suptag(tree, tree.root, hieght_dict, path_dict)
        print sorted([(tree[k].identifier, tree[k].tag, v) for k,v in path_dict.items()])


        
   #     stags = {}
   #     get_suptag_topdown(tree, tree.root, False, stags)
   #     print map(lambda leaf: (leaf.tag, stags[leaf.identifier]), tree.leaves())
   #


if __name__ == '__main__':
    
    #toy_demo()
    wsj_demo()
 
                


    
