#!/usr/bin/env python

from setuptools import setup

setup(name='RNAseq_analysis_tools',
      version='0.1',
      description='Tools for analyzing RNAseq counts data, including heirarchical clustering, heatmaps, and PCA',
      author='Meaghan Flagg',
      author_email='mfskibum@gmail.com',
      license="huh, hadn't thought of that", #check
      packages=['RNAseq_analysis_tools'],
      zip_safe=False # what is this?
      install_requires=['scipy', 'numpy', 'pandas'],  # dependencies. Can specify versions: 'scipy==0.19', or pandas>=0.23' etc
      )

