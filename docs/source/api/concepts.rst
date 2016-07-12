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
--------

All of checkmate's functionality is exposed through **commands**. All commands inherit form a `:ref:BaseCommand`
class and accept a range of parameters. Currently there are commands to deal with file-based projects, as well as 
`git` projects.

Command Chaining
----------------

Often we want to combine several individual commands into a chain. As an example, we could use the
`git` command to select a number of snapshots, then use the `analyze` command to analyze them and
finally send a summary of the analysis via e-mail using the `email` command. In the shell world, the
pipe (`|`) operator is used for sending the output of one command as input to another command.

In checkmate, the command parser performs this function by looking for a command name in the sequence
of parameters. It then executes each command in turn, providing it the options that have been specified
to it as well as the output of the previous command(s) as its input. For example,

.. code::

    checkmate git --branch master --n 4 analyze --analyzers pylint

would first execute the `git` command with parameters `branch=master` and `n=4` and then the `analyze`
command with the parameters `analyzers=pylint` as well as the output of the `git` command.

Event Hooks
-----------

Commands can emit events to which plugins can attach themselves via hooks. The purpose of these hooks
is to allow the plugin to intercept, work with and possibly modify the state of a command at a given
moment. Events and hooks work as follows:

* To emit an event, a `Command` class just calls the `emit` function of the `BaseCommand` class,
  which accepts a `name` argument as well as an arbitrary number of additional parameters.
  The return value of that call is a dictionary that contains the return values of all handler
  functions that responded to the event, where the key corresponds to the name of the plugin.
* A plugin can subscribe to various hooks by specifying a `hooks` dictionary in its `setup` module.
  The keys in this dictionary should correspond to the name of the hooks that the plugin wants to
  listen to and the values to the return values of the function calls.
  If one of the hook functions throws an exception it will be recorded. When all hook functions
  have been executed, a `HookException` exception will be thrown that contains a dictionary with
  the individual exceptions thrown by all hook functions.
* When an event is emitted, each hook function listening to that event will be called with the
  following arguments:

    * The command instance that has emitted the event call
    * The parameters that the command has passed to the event function
