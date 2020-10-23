# Matplotlib Cheatsheet
Handy guide for commonly used plotting parameters using matplotlib and seaborn  
Author: Meaghan Flagg

### Import conventions:
`import matplotlib.pyplot as plt`  
`import seaborn as sns`  

### Quick and easy figure initialization
`fig, ax = plt.subplots()`
* can pass ncols=n, nrows=n to create fig with mutltiple subplots (ax becomes list object)
* can pass figsize=(x,y)


### Adjust x and y ticks:
Two sets of functions from matplotlib: tick *locator* and tick *formatter*.
* https://matplotlib.org/3.1.1/gallery/ticks_and_spines/tick-locators.html
* https://matplotlib.org/3.2.1/gallery/ticks_and_spines/tick-formatters.html
* major and minor ticks

```python
import matplotlib.ticker as ticker
ax.yaxis.set_major_loctor(ticker.NullLocator())
ax.xaxis.set_major_formatter(ticker.PercentFormatter())
```
`ticker.FuncFormatter()` allows you to pass a custom function to format your ticklabels.

### Customize plot appearance:
Hide spines:  
`sns.despine(top=True, right=True) # using seaborn`  
`ax.spine['right'].set_visible(False) # matplotlib`  

### Text properties:
https://matplotlib.org/3.2.1/tutorials/text/text_props.html  
pass a kwargs to text functions, or create dictionary to pass to fontproperties argument  
`family : [ 'serif' | 'sans-serif' | 'cursive' | 'fantasy' | 'monospace' ]`  
`style` or `fontstyle : [ 'normal' | 'italic' | 'oblique' ]`  
`weight` or `fontweight :	[ 'normal' | 'bold' | 'heavy' | 'light' | 'ultrabold' | 'ultralight']`

### Modify legends and create custom legends:
Hide legend:  
`ax.legend().remove()`  

Adjust properties of existing legend:  
`ax.legend(handles=handles, labels=labels, **kwargs`  
https://matplotlib.org/3.2.1/api/_as_gen/matplotlib.axes.Axes.legend.html  
* legend location:  
   * `loc='center left'` general location, or reference loc when using bbox_to_anchor
   * `bbox_to_anchor=(0,1)` enter location in x,y coordinates. defaults to axes coordinates  
* legend appearance:
   * `frameon=False` remove outside frame
   * `ncol=2` wrap legend items in multiple columns
   * `prop={}` fontproperties dict
   * `fontsize=12`

#### Custom markers:
* https://matplotlib.org/users/legend_guide.html#creating-artists-specifically-for-adding-to-the-legend-aka-proxy-artists
* `import matplotlib.lines as mlines`
* use `Line2D` object instead of marker object
* set `linestyle='None'` (quotes required)

#### Custom patches:
* `import matplotlib.patches as mpatches`
* enclose patches in list, pass to 'handles' argument of `ax.legend()`:
  * `mpatches.Patch(facecolor='color', **kwargs)`

### FacetGrid with Seaborn:
Very useful to generate multiple plots for a set of categorical variables. Input should be a long-form pandas dataframe (`pd.melt()`)

**Initialize FacetGrid object and define parameters:**  
`g=sns.FacetGrid(data=data, row=row_var, col=col_var, **kwargs)`  
`g.map(sns.boxplot, 'x_var', 'y_var', 'hue_var', **kwargs)` : pass plotting function, x variable name, y variable name, and hue variable name as positional arguments. You can then pass other function-specific (e.g `sns.boxplot`) keyword agruments.

**Control FacetGrid attributes:**  
`g.fig.tight_layout()`  
`g.add_legend()`  
`g.set_titles("{col_name}")` String formatter for plot titles. Can refer to row and column variable names using `{row_name}` or `{col_name}`.

**Access individual facets or control facet-level attributes:**  
```python
for ax in g.axes.flatten(): # bulk operations
  ax.tick_params(labelbottom=True, axis='x') # make labels visible on all facets
  ax.set_ylabel()

for i, ax in enumerate(g.axes.flat): # access individual facets
  if i in [1,2,3]:
    ax.xaxis.set_major_formatter(ticker.PercentFormatter())

```
