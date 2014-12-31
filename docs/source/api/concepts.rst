Core Concepts
=============

This document gives a brief overview of the main concepts and models that Checkmate uses to analyze your code.

Checkmate uses a document-oriented data model to store information about a given project. The underlying model is very simple and allows us to model projects managed through various version control systems such as git. The model defines the following classes:

Project
-------

A project contains the information about a given code repository, e.g. file revisions, snapshots, issues and diffs. This will create a `.checkmate` folder
either in your current working directory, or, if you call it inside a git repository, in the directory that
contains the `.git` folder. You project consists of all files contained in the directory that contains 
the `.checkmate` folder (including all subdirectories).

Snapshot
--------

A snapshot represents the state of your entire project or a subset of the project at a given point. This can be
e.g. a certain git commit or just the local state of the project directory at a given time. Snapshots are generated
through the `checkmate analyze` command.
 
File Revision
-------------

A file revision describe the state of a file at a given point. It contains both statistics as well as a list of
issues for the given file. To create a snapshot, several file revisions are bundled together.

.. warning::

   The concept of a file revision used here is more general than that of e.g. Git or Subversion. Most importantly, two file revisions can have the exact same content and still be considered as different. This is for example the case if file A imports a function from file B. Since A depends on B, changes in B will possibly impact the functionality defined in A. Thus, whenever file B changes we will check file A (even if it hasn't changed itself) and
   create a new file revision for it.

Issue
-----

An issue is a description of a particular code problem. Each issue description provides an issue code and analyzer
name, as well as information about the location of the issue (i.e. file revisions and line numbers). The issue's meta-data (e.g. severity, categories, ...) is stored externally. An issue is always associated with a given file revision. Multiple occurences of the same issue type will usually get bundled together, i.e. only one issue document will be created for all occurences of that issue in a given file.

Commands
========

All of checkmate's functionality is exposed through **commands*+. All commands inherit form a `:ref:BaseCommand`
class and accept a range of parameters. Currently there are commands to deal with file-based projects, as well as 
`git` projects.

Analyzing a Snapshot
====================

When you run `checkmate analyze`, the following things happen behind the scenes:

* checkmate generates a list of all the files matching your analysis request
* it checks which of these file revisions have not yet been analyzed
* it analyzes the missing file revisions and stores the results in its database
* it creates a snapshot from the file revisions

Like this, checkmate makes sure to never analyze the same file twice, which greatly improves the performance
of the tool when running it against a large codebase.

Dependencies
============

When `checkmate` analyzes a snapshot, it tries to use results from previous runs to analyze as
few file revisions as possible. To make this possible, it needs to know about a file's dependencies.

For this, each file revision contains a `dependencies` list. Each entry there contains
meta-data for that dependency, which allowS `checkmate` to localize it.

Hence, when a new snapshot gets analyzed, the following procedure applies:

1) Get a list of all file revisions in the snapshot
2) Get a list of all existing as well as all modified file revisions
3) Add all modified file revisions to the list of file revisions to be analyzed (the **analyze list**)
4) For all of the other file revisions, resolve the dependencies of each one and check 
   if a given dependency is contained in the **analyze list**.
4) If it does, add the file revision to the **analyze list**
5) Repeat 4) until the **analyze list** no longer changes.