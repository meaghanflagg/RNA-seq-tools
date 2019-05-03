#!/usr/bin/env python

'''
Generate volcano plot from csv file containing DESeq2 results
Built for python 2.7
'''
# boring stuff:
__author__ = "Meaghan Flagg"
__email__ = "mfskibum@gmail.com"
__version__ = "0.1"
__status__ = "development"



# import required modules
import argparse
import pandas as pd
import numpy as np
import plotly as py
import plotly.graph_objs as go
import plotly.tools as tls


def significance_foldchange_cutoffs(df, pval_thresh=0.5, foldchange_thresh=1.5):
    # requires column name info from DESeq2
    significant_hits=df[(df['padj'] < pval_thresh) & (abs(df['log2FoldChange']) > foldchange_thresh)]
    nonsig_hits=df.loc[~df.index.isin(significant_hits.index)]
    return significant_hits, nonsig_hits



def plot_volcano(significant_hits, nonsignificant_hits, filename, title=None, annotation_col=None):
    
    # create annotation text: (must be done explicitly for signifant and nonsignificant hits, since they are different dfs)
    if annotation_col == None:
        annotation_text_ns=nonsignificant_hits.index
        annotation_text_sig=significant_hits.index
    else:
        annotation_col.append('index')  # allows retention of index info after reset_index() is applied in next step
        try:
            annotation_text_ns = nonsignificant_hits.reset_index()[annotation_col].apply(lambda x: ' ; '.join(x.astype(str)), axis=1)
            annotation_text_sig = significant_hits.reset_index()[annotation_col].apply(lambda x: ' ; '.join(x.astype(str)), axis=1)
        except KeyError:
            annotation_text_ns=nonsignificant_hits.index
            annotation_text_sig=significant_hits.index
    
    
    # title setup:
    if not title:
        title=filename
    

    non_sig_trace = go.Scatter(x=nonsignificant_hits['log2FoldChange'], y=-np.log10(nonsignificant_hits['padj']),
                      marker={'color':'black', 'symbol':'dot', 'size': '8'}, hoverinfo='text',
                      mode='markers', text=annotation_text_ns, name='non-significant')
    sig_trace=go.Scatter(x=significant_hits['log2FoldChange'], y=-np.log10(significant_hits['padj']), 
                      marker={'color':'red', 'symbol':'dot', 'size': '8'}, hoverinfo='text',
                     mode='markers', text=annotation_text_sig, name='significant hits')
    
    data=go.Data([non_sig_trace, sig_trace])
    layout=go.Layout(title=title, xaxis={'title':'log2FoldChange'}, yaxis={'title':'-log10(padj)'}, hovermode='closest')
    figure=go.Figure(data=data, layout=layout)
    
    # filename setup:
    if not filename.endswith(".html"):
        filename=filename+".html"
    
    py.offline.plot(figure, filename=filename, auto_open=False)

def main():
    parser=argparse.ArgumentParser()   
    # required arguments
    requiredArgs = parser.add_argument_group('required arguments')
    requiredArgs.add_argument("-data", type=str, help="DESeq2 results file in CSV format", required=True)
    requiredArgs.add_argument("-out", type=str, help="Output filename for plot", required=True)
    # optional arguments
    parser.add_argument("-title", type=str, default=None, help="plot title. Defaults to filename")
    parser.add_argument("-annotation_col", type=str, nargs='+', default=None, help="Name(s) of column(s) (separated by spaces) containing additional annotation info for hover text. Index info is always included by default.")
    parser.add_argument("-pval_thresh", type=float, default=0.5, help="threshold p-value for significant hits")
    parser.add_argument("-foldchange_thresh", type=float, default=1.5, help="threshold foldchange (absolute value) for significant hits")
    parser.add_argument("-header", type=int, default=0, help="Specify header row. Explicitly pass 'None' if there is no header") # figure out how to deal with files missing header info
    parser.add_argument("-index_col", type=int, default=0, help="Specify index column. Explicitly pass 'None' if there is no index column")
    
    args=parser.parse_args()
    
    data=pd.read_csv(args.data, header=args.header, index_col=args.index_col)
    
    
    # extract significant and nonsignificant hits:
    sig, nonsig = significance_foldchange_cutoffs(data, pval_thresh=args.pval_thresh, foldchange_thresh=args.foldchange_thresh)
    
    # plot it:
    plot_volcano(sig, nonsig, args.out, title=args.title, annotation_col=args.annotation_col)

if __name__ == '__main__':
    main()
    


