:orphan:

.. title:: Welcome to Checkmate!

.. raw:: html

   <h1><i class="fa fa-check-circle" style="color:#0a5;"></i> Welcome to Checkmate!</h1>

**Checkmate** is Python tool for code quality management. It gives you a global overview of the code
quality in your project and provides you with actionable insights and advice.

Motivation
----------

Most current command-line tools for code quality management overburden the user
with too much information, are hard to set up and adapt to the users needs and do not provide enough actionable insight.

Checkmate is an attempt to change this: 

* It doesn't overwhelm your with tons of irrelevant information. 
* It provides clear, actionable advice and a global view of your code quality.
* It wraps several code checking tools, providing a consolidated view on their data.

Key Features
""""""""""""

* Global statistics and issue lists for your project.
* Actionable, prioritized advice on how to improve the code.
* Built-in support of popular code checkers (**pep8**, **pylint** and **pyflakes**)
* Easily extendable and adaptable to your needs.
* Tracking of metrics and issues over time.
* Automatic versioning of your source files.
* Built-in support for git repositories.

Installation
------------

The easiest way to install checkmate is via **pip** or **easy_install**:

.. code-block:: bash

    pip install 7s-checkmate

or

.. code-block:: bash

    easy_install 7s-checkmate

Alternatively, you can just download the source from Github and install it manually by running (in the project directory):

.. code-block:: bash

    git clone git@github.com:adewes/checkmate.git
    cd checkmate
    python setup.py build
    sudo python setup.py install

Quickstart
----------

After installation, you should have a new **checkmate** command available in your shell. The command line interface (CLI) of checkmate is similar to that of **git**, so if you're familiar with the latter you should feel at home pretty fast.


Creating a new project
""""""""""""""""""""""

To create a new checkmate project, just go to your project folder and type:

.. code-block:: bash
    
    checkmate init

If run inside a git repository, this will create a new checkmate project in the root folder of the git project. Otherwise it will create a project in the current directory. Like *git*, *checkmate* keeps all its files in a *.checkmate* folder.

Analyzing your code
"""""""""""""""""""

To analyze your projects and produce metrics and issue lists, simply type:

.. code-block:: bash
    
    checkmate analyze

This will generate of relevant files in your project, analyze them and generate a summary of the results. You can use on of the following commands to work with the results of the analysis:

.. code-block:: bash

    #Shows a summary of statistics and issues for your project
    checkmate summary
    #Show a list of issues for your project
    checkmate issues
    #Show a summary of the statistics & metrics of your project
    checkmate stats

There are some other commands you might find useful, for more information about the available commands or a specific command, just type

.. code-block:: bash

    #Provides an overview of all commands and options
    checkmate help
    #Provides information about a specific command
    checkmate help [command name]

.. raw:: html

    <a href="https://github.com/adewes/checkmate"><img style="position: absolute; top: 0; right: 0; border: 0;" src="https://github-camo.global.ssl.fastly.net/652c5b9acfaddf3a9c326fa6bde407b87f7be0f4/68747470733a2f2f73332e616d617a6f6e6177732e636f6d2f6769746875622f726962626f6e732f666f726b6d655f72696768745f6f72616e67655f6666373630302e706e67" alt="Fork me on GitHub" data-canonical-src="https://s3.amazonaws.com/github/ribbons/forkme_right_orange_ff7600.png"></a>

.. include:: contents.rst.inc
