#!/usr/bin/env python

'''
my code for extracting the 8-bp barcode from nextera primer sequences

Primer structure:
i5: AATGATACGGCGACCACCGAGATCTACAC <8bp barcode> TCGTCGGCAGCGTCAGATGTG
i7: CAAGCAGAAGACGGCATACGAGAT <8bp barcode> GTCTCGTGGGCTCGGAGATGT

(I figured this out by aligning multiple primer sequences using Ape)


'''

def extract_i5_barcode(barcode):
    return barcode.split('AATGATACGGCGACCACCGAGATCTACAC')[1].split('TCGTCGGCAGCGTCAGATGTG')[0]

def extract_i7_barcode(barcode):
    return barcode.split('CAAGCAGAAGACGGCATACGAGAT')[1].split('GTCTCGTGGGCTCGGAGATGT')[0]

def extract_i5_rc_barcode(barcode):
    '''
    extracts reverse complement of i5 index from nextera primer sequence.
    Depends on biopython Seq and Alphabet modules
    
    Imports:
    
    from Bio.Seq import Seq
    from Bio.Alphabet import generic_dna
    '''
    from Bio.Seq import Seq
    from Bio.Alphabet import generic_dna
    index=barcode.split('AATGATACGGCGACCACCGAGATCTACAC')[1].split('TCGTCGGCAGCGTCAGATGTG')[0]
    dna_object=Seq(index, generic_dna)
    return str(dna_object.reverse_complement())

# these files are located in ~/Documents/Kwon_lab/Nextera_deets
i7 = pd.read_excel("Nextera_index_sequences.xlsx", sheetname=1, parse_cols="B:F", header=1, skip_footer=4)

i5=pd.read_excel("Nextera_index_sequences.xlsx", sheetname=0, parse_cols="B:G", header=1, skip_footer=6)

# apply functions to extract barcode:
i5['barcode'] = i5['Sequence'].map(extract_i5_barcode)


i7['barcode'] = i7['Sequence'].map(extract_i7_barcode)

# write to excel file with multiple sheets:

writer = pd.ExcelWriter('nextera_barcodes.xlsx')
i5.to_excel(writer, sheet_name='i5')
i7.to_excel(writer, sheet_name='i7')
writer.save()

# use biopython to get reverse complement (necessary for i5 indexes on next seq)

from Bio.Seq import Seq
from Bio.Alphabet import generic_dna

i5['barcode_rc'] = i5['Sequence'].map(extract_i5_rc_barcode)

# write this out if you want
