#!/usr/bin/env python


def files_list_from_dir(directory, glob_pattern):
    import os, fnmatch
    files_list=[]
    for f in os.listdir(directory):
        if fnmatch.fnmatch(f, glob_pattern):
            files_list.append(os.path.join(os.path.abspath(directory),f))
    return files_list


def rename_file(filename):
    return

if __name__ == '__main__':
    import json, argparse, sys
    parser = argparse.ArgumentParser(description="DESCRIPTION: rename slurm .out and .err logs with filename info")
    parser.add_argument("-dir", type=str, default=os.getcwd(), help="path to directory containing log files. Default: current working directory")
    parser.add_argument("-json", type=str, help="path to json file containing SLURM_ARRAY_TASK_ID:filename dictionary. Required.")
    
    args=parser.parse_args()
    
    if not args.json:
        sys.exit("'-json' argument is required. ")
    
    outlogs=files_list_from_dir(args.dir, "*.out")
    errlogs=files_list_from_dir(args.dir, "*.err")
    
    outlog_regex=r'[0-9]+.out'
    errlog_regex=r'[0-9]+.err'
    
    