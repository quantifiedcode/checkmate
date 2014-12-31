Git Integration
===============

Checkmate plays nicely with the *git* version control system. All command working with git repositories are contained in
the **git** command group, for example:

.. code-block:: bash

    #analyzes the last commits from a git project
    checkmate git analyze

    #resets a git project
    checkmate git reset

Setting Up SSH
--------------

Checkmate can use user-provided SSH keys to access git repositories over SSH. For this, `checkmate.lib.git.repository.fetch` 
overrides the default SSH agent with `checkmate/lib/git/ssh`, which passes in the identity file given to `fetch`.

.. warning::

    For security reasons, you should disable all default identities for the user that runs this command, since your SSH client
    will otherwise try all keys available to this user when accessing a repository, thereby possibly compromising the security
    of your private repositories

SSH config
------------------

By default, the SSH agent invoked by the `fetch` command will generate and use a configuration file that looks like this:

.. code-block:: bash

    Host *
         StrictHostKeyChecking no
         IdentityFile [path/to/identity/file]
         IdentitiesOnly yes

Here,`StrictHostKeyChecking` is disabled and `IdentitiesOnly` enabled. The identity file is the file given through the `identity_file` parameter of the `fetch` method.