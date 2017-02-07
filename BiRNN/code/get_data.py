from __future__ import print_function
from read_trees import write_trees
import os
import shutil
import sys



def combine_all_trees(in_data_path, out_data_path):
    
   # for source in ['wsj', 'HTML']:
#    if (not os.path.exists(os.path.join(out_data_path, source))):
    if (not os.path.exists(os.path.join(out_data_path, source))):
        filenames = []
        for d in ["{:02d}".format(x) for x in xrange(25)]:
            for f in os.listdir(os.path.join(in_data_path, source, d)):
                filenames.append(os.path.join(in_data_path, source, d, f))

        with open(os.path.join(out_data_path), 'w') as outfile:
            for fname in filenames:
                with open(fname) as infile:
                    for line in infile:
                        outfile.write(line)

def get_miss(src_dir):

    miss_list =[]
    for sub_dir in os.listdir(src_dir):
        for f_in in os.listdir(os.path.join(src_dir, sub_dir)):
            src = os.path.join(src_dir, sub_dir, f_in)
            my_file = open(src, 'r') 
            if my_file:
                current_line = my_file.readline()

            for line in my_file:   
                previous_line = current_line
                current_line = line
                if ("no CCG derivation" in line):
                    miss_list.append(previous_line.partition('"')[2].partition('"')[0])

    with open("miss_out", 'w') as x_file:
        for elm in miss_list:
            x_file.write(elm+"\n")

    return miss_list

def del_miss_lines(src_dir, in_dir):


    print("[del_miss_lines] Deleting missing untagged sentances in CCG")
    
    miss_list = get_miss(src_dir)

    for mline in miss_list:
        for k,v in {"trees": ".mrg.tr", "words" : ".mrg.wrd"}.items():
            my_file = os.path.join(in_dir, "tags", mline.partition("_")[2][:2],k, mline.partition(".")[0]+v)
            line_to_del = mline.partition(".")[2]
            f = open(my_file,"r+")
            d = f.readlines()
            f.seek(0)
            for i, l in enumerate(d,1):
                if i != int(line_to_del):
                    f.write(l)
            f.truncate()
            f.close()
                       

def make_dir(path_dir):
    
    if not os.path.exists(path_dir):
        try:
            os.makedirs(os.path.abspath(path_dir))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

#TODO: hidden files
def del_extra_files(root_dir):

    print("[del_extra_files] Deleting mismatching files between dirs")
    
    for f in os.listdir(root_dir):
        if os.path.isdir(os.path.join(root_dir, f)) and f not in ["{:02d}".format(x) for x in xrange(25)]:
            shutil.rmtree(os.path.join(root_dir, f))
        if os.path.isfile(os.path.join(root_dir, f)):
            os.remove(os.path.join(root_dir, f))

#TODO: hidden files
def del_diff_files(root_dir):
    
    print("[del_diff_files] Deleting mismatching files between dirs")
    
    for d in ["{:02d}".format(x) for x in xrange(25)]:
        wsj  = [f.partition('.')[0] for f in os.listdir(os.path.join(root_dir, 'wsj', d))]
        HTML = [f.partition('.')[0] for f in os.listdir(os.path.join(root_dir, 'HTML', d))]

        diff = set(wsj).union(set(HTML))-set(wsj).intersection(set(HTML))
        for f in list(diff.intersection(set(wsj))):
            os.remove(os.path.join(root_dir, 'wsj', d,  f + '.mrg'))
        for f in list(diff.intersection(set(HTML))):
            os.remove(os.path.join(root_dir, 'HTML', d, f + '.html'))

def get_data(data_path):

    print("[get_data] Getting RAW data from corpora")

    make_dir(data_path)
    
    for k,v in { 'wsj': 'EnglishTreebank/wsj/ ', 'HTML': 'ccgbank_1_1/data/HTML/ '}.items():
        if not os.path.exists(os.path.join(data_path, k)):
            os.system("scp -r login.eecs.berkeley.edu:/project/eecs/nlp/corpora/"+ v + data_path)
            del_extra_files(os.path.join(data_path, k))
    del_diff_files(data_path)


def reformat_file(file_in, out_dir, fname):

   # print("[reformat_file] Reformating HTML file")
    
    make_dir(out_dir)

    f_out   = os.path.join(out_dir, fname + '.mod')      
    f_in    = open(file_in, 'r')    
    s       = "" 
    with open(f_out, 'w') as fout:
        for line in f_in:  
            if (line.strip()=='<pre>'):
                line = next(f_in, None)
                while (not '</pre>' in line):
                    if line.strip():
                        s = s + line.split('\n')[0]
                    line = next(f_in, None)
                print("{"+s+"}" , file = fout)
                s =  ""

def reformat_dirs(src_dir, out_dir):

    print("[reformat_dirs] Reformating HTML files")

    dest_dir = os.path.join(out_dir, "stags", "raw")
    for sub_dir in os.listdir(src_dir):
        d_dir = os.path.join(dest_dir, sub_dir)
        for f_in in os.listdir(os.path.join(src_dir, sub_dir)):
            src = os.path.join(src_dir, sub_dir, f_in)
            reformat_file(src, d_dir, f_in)
    return dest_dir                


def generate_trees(src_dir, dest_dir, _SB, _EB):

    print("[generate_trees] Generating trees and words")
    
    for sub_dir in os.listdir(src_dir):
        out_path = os.path.join(dest_dir, sub_dir)
        make_dir(os.path.join(out_path, "trees"))
        make_dir(os.path.join(out_path, "words"))
                    
        for f_in in os.listdir(os.path.join(src_dir, sub_dir)):
            data_in =  os.path.join(src_dir, sub_dir, f_in)
            tree_out =  os.path.join(out_path, "trees", f_in+'.tr')
            word_out =  os.path.join(out_path, "words", f_in+'.wrd')
            
            write_trees(tree_out, word_out, open(data_in, 'r'), _SB, _EB)

 
    
if __name__ == '__main__':
    
#    args = sys.argv[1:]
#    if len(args) != 2:
#        print('Usage: python3 get_data.py path/to/read/raw/data path/to/write/modified/data ')
#    raw_data_path, mod_data_path = args
#
#    get_data(raw_data_path)
#    source_stag     = reformat_dirs(os.path.join(raw_data_path, "HTML"), mod_data_path)
#
#    source_dir  = {"tags": os.path.join(raw_data_path, "wsj"), "stags": source_stag}  
#    br = {"tags": ['(',')'], "stags": ['{','}']}
#    for tag in ["tags", "stags"]:
#        dest_dir    = os.path.join("mod_data", tag)
#        generate_trees(source_dir[tag], dest_dir, br[tag][0], br[tag][1])
#
#    del_miss_lines(os.path.join(raw_data_path, "HTML"), mod_data_path)

#    combine_all_trees(raw_data_path, mod_data_path)
   
    get_miss(os.path.join("raw_data", "HTML"))
    





    
