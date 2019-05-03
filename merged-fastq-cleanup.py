#!/usr/bin/env python

import sys

f1=open(sys.argv[1],'r')
f2=open(sys.argv[2],'w')

for line in f1:
    if line.startswith("@"):
        f2.write(line+f1.next()+f1.next()+f1.next())
        
f1.close()
f2.close()
