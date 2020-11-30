# Plotly Cheatsheet
Handy guide for commonly used plotting parameters using plotly in python  
Author: Meaghan Flagg

### Import conventions:
```python
import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot # maybe not necessary
init_notebook_mode(connected=True)
```

### Basic plot using plotly express:
```python
fig = px.scatter(data_frame=df, x='x_var', y='y_var',
  color='hue_var', color_discrete_map=dictionary, hover_name='df_column')
```
Notes:
* can also pass list/array to `hover_name=`
* can customize plot appearance with `template=`:
---
### Customization:
Available themes:  

* `["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]`
* https://plotly.com/python/templates/  

Set default themes:
```python
import plotly.io as pio
pio.templates.default = "plotly_white"
```
Using update layout:
```python
fig=px.scatter()
fig.update_layout(template='template', title='title', **kwargs)
```
