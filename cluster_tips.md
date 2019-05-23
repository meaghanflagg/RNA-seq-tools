# Tips for working effectively on the HMS O2 cluster
for general information on the HMS O2 cluster please reference the wiki: https://wiki.rc.hms.harvard.edu/display/O2

### Customize your .bashrc file:
* automatically load frequently used modules at login
* add a set of custom scripts to your path
* add helpful aliases for common commmands, such as ls

### Using Conda on the cluster:
* https://wiki.rc.hms.harvard.edu/display/O2/Conda+on+O2

* load the conda module and create an environment:  
`module load conda`  
`conda create -n my_env`  

* list existing environments:  
`conda info --envs`

* activate/deactivate an environment:  
`source activate my_env`  
`deactivate my_env`

* install a package from conda:  
`conda search numpy` (search for the package in conda channels)  
`conda install numpy` (you must do this from inside an active conda environment, or you will not have permission)

* install a package not available on conda (e.g. github)  
`git clone package`
`source activate my_env` (activate the env you want the package installed in)  
`pip install ./package`
