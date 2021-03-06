# yaml2sbml


[![Build Status](https://travis-ci.org/martamatos/yaml2sbml.svg?branch=master)](https://travis-ci.org/martamatos/yaml2sbml)
[![Coverage Status](https://coveralls.io/repos/github/martamatos/yaml2sbml/badge.svg)](https://coveralls.io/github/martamatos/yaml2sbml)


Table of contents
-----------------

* [Introduction](#introduction)
* [Installation](#installation)
* [Usage](#usage)
* [Known issues and limitations](#known-issues-and-limitations)



Introduction
------------

yaml2sbml is a small package to convert an ODE model specified in a yaml file into an SBML, that can be used with other packages.

Examples can be found in the `examples` folder.



Installation
-------------


To install go to the main folder and do:

```pip install .```


## Requirements

 - Python 3.6+
 - python-libsbml>=5.18.0
 - PyYAML>=5.3


#### Requirements files:
 - `requirements.txt` 
 

#### How to get Python 3.6+
If you don't have Python 3.6 or higher in your system, the best way to get it is either using pyenv or conda.
 
With conda you can create a virtual environment with a specific python version. To do so start by installing miniconda if you don't have any sort of conda installed yet, and then create a virtual environment using a specific version of python:

``` conda create -n <virtual_env_name> python=3.7```

To activate the virtual environment do

``` source activate <virtual_env_ńame>```

To install packages use either pip or conda: 

``` conda/pip install <package_name> ```


Usage
-----

To convert an ODE model encoded in a yaml file to SBML using the terminal, go to the `yaml2sbml` folder and run:

```
 python yaml2sbml.py <yaml_input_file> <sbml_output_file>
```

For instance, using the yaml file in the examples folder:

```
 python yaml2sbml.py ../examples/ode_input1.yaml ../examples/sbml_out.xml
```



Known issues and limitations
------------------------------

 - Compartments are not supported.
 - Units are not supported, all quantities are dimensionless.
