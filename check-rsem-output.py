#!/usr/bin/env python

import os, sys, fnmatch


def check_rsem_output(results_directory):
    '''
    usage:
    python check-rsem-output [directory]
    
    searches recursively through specified directory (default=pwd) for directories with rsem outputs (defined by directories containing a ".stat" directory)
    flags directories as possible failures if the do not contain a ".genes.results" file, or if they do still contain a ".temp" file
    '''
    
    
    flagged_directories=[]
    for path, subdirs, files in os.walk(results_directory):
        for s in subdirs:
            if fnmatch.fnmatch(s, '*.temp'):
                flagged_directories.append(path)
    
    output_directories=[]
    for path, subdirs, files in os.walk(results_directory):
        for s in subdirs:
            if fnmatch.fnmatch(s, '*.stat'):
                output_directories.append(path)
                
    successful_directories=[]
    for path, subdirs, files in os.walk(results_directory):
        for f in files:
            if fnmatch.fnmatch(f, '*.genes.results'):
                successful_directories.append(path)
                
    # get any path in output_directories that is not in successful_directories
    failed=set(output_directories).difference(set(successful_directories))
    
    combined_flagged_dirs=set(flagged_directories).union(failed)
    num_output_dirs=len(output_directories)
    
    return combined_flagged_dirs, num_output_dirs

if __name__ == '__main__':
    try:
        if sys.argv[1] in ["-h","--help"]:
            sys.exit(check_rsem_output.__doc__)

        results_directory=sys.argv[1]
    except IndexError:
        results_directory=os.getcwd()
    
    combined_flagged_dirs, num_output_dirs=check_rsem_output(results_directory)
    
    print "Scanning {0} for RSEM output files.".format(results_directory)
    print "Found {0} output files/directories.".format(num_output_dirs)
    if len(combined_flagged_dirs) > 0:
        print "Flagged the following directories as 'failed':"
        print "\n".join(combined_flagged_dirs)
    else:
        print "no errors found."
    print "analysis complete"

