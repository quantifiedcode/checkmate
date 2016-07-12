Dependency Management
=====================

Checkmate allows analyzers to define file revision dependencies. This allows to see exactly which
other file revisions might be affected by a change in a given file revision. The format for
defining a dependency is as follows:

.. code::

    {
        'type' : 'import',
        'module' : 'foo.bar',
        'imported_names' : ['foo','bar','baz'],
    }

Here, we know that the given module imports another module named `foo.bar`, and more specifically
that it imports the three names `foo`, `bar` and `baz` from that module. Now if in a given analysis,
the file revision that resolves to the module has been modified, we know that we will also have to
analyze the dependent file revision.

The dependency resolution process is thus as follows:

* For a given snapshot, we generate a list of all modified file revisions.
* For all other file revisions, we check the dependencies and resolve them to file revisions.
* If an unmodified file revision has a dependency that maps to a modified one, we add it to the
  list of modified file revisions.
* We repeat this process until no new files have been added to the list of modified files.

Dependency Resolution
=====================

To resolve dependencies, we need to know about the Python module system. Information about import
paths and additional, external dependencies will be read from the project whenever possible. You can
also specify these within the `.checkmate.yml` file.

