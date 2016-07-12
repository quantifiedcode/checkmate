## How to contribute

Contributions are very welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

### Contributor Licence Agreement

We are asking all past and future contributors to sign a Contributor License Agreement (CLA). Every contributor of non-trivial amounts of code (more than just a line or two) to checkmate is required to sign a CLA. If somebody is unable to sign the CLA, the contribution (e.g., code, documentation, translations) has unfortunately to be removed from checkmate.

The CLA ensures that QuantifiedCode has clear licensing for all contributions to checkmate, which in turn lets us guarantee to users that we have no "stray" intellectual property or differently-licensed material.

**Where do I sign? What's next?**

1. Download a copy of the CLA:

    * [Individual Contributor License Agreement (PDF)](https://github.com/quantifiedcode/checkmate/raw/master/contributing/icla.pdf): If you're working on checkmate as an individual, this is the form you should use.
    * [Entity Contributor License Agreement (PDF)](https://github.com/quantifiedcode/checkmate/raw/master/contributing/ecla.pdf): If you're working on checkmate as part of your job, you and your employer will need to download and sign this form.

2. Print out the CLA and sign it.

3. Send the CLA to QuantifiedCode by scanning and emailing the document to [cla@quantifiedcode.com](cla@quantifiedcode.com)

### Type of contributions

#### Report Bugs
Report bugs at [https://github.com/quantifiedcode/checkmate/issues](https://github.com/quantifiedcode/checkmate/issues).

If you are reporting a bug, please include:

* The trackeback of the error
* Your operating system name and version
* Any details about your local setup that might be helpful in troubleshooting
* Detailed steps to reproduce the bug
* A screenshots (if useful)

#### Fix Bugs
Go through the [Github issues](https://github.com/quantifiedcode/checkmate/issues). Anything that is tagged as "bug" is open to whoever wants to implement it.

#### Add new features
Go through the  [Github issues](https://github.com/quantifiedcode/checkmate/issues). Anything tagged as "feature" is open to whoever wants to implement it.

#### Write Documentation
Checkmate can always get more documentation, whether as part of the official checkmate [https://docs.quantifiedcode.com](https://docs.quantifiedcode.com), in docstrings, or even on the web in blog posts,
articles, and such.

#### Submit Feedback and Propose Features
The best way to send feedback is to file an issue at [https://github.com/quantifiedcode/checkmate/issues](https://github.com/quantifiedcode/checkmate/issues). Additionally, you can reach out to our [team](https://www.quantifiedcode.com/team). We are looking forward getting in touch with you!

If you are proposing a feature:
* Detailed description of the feature to be implemented
* [User story](https://en.wikipedia.org/wiki/User_story) (if applicable)
* Keep the scope as narrow as possible, to make it easier to implement
* Remember that this is a volunteer-driven project, and that contributions are welcome :)

## Get Started!
Are you ready to contribute? Here's how to set up `checkmate` for local development.

1. First, make sure [MongoDB](http://docs.mongodb.org/manual/installation/) is installed on your machine.

2. Fork the `checkmate` repo on GitHub.

3. Clone your fork locally:

        $ git clone git@github.com:<your_github_user_name>/checkmate.git

4. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development:

        $ mkvirtualenv checkmate
        $ cd checkmate/
        $ python setup.py

5. Create a separate branch for each issues in your local development environment:

        $ git checkout -b issue/<issue_id>_<issue_title>

        Example:$ git checkout -b issue/112_add_jslint

6. Now, make your changes locally.

7. When you're done with your changes, please commit and push them to your branch:

        $ git add .
        $ git commit -m "Fix <issue_id>: detailed description of your changes."
        $ git push origin issue/<issue_id>_<issue_title>

8. Submit a Pull Request through the GitHub website.

## Pull Request Guidelines

Before you submit a Pull Request, check that it meets these guidelines:

1. Check on [https://www.quantifiedcode.com/app#/project/gh:quantifiedcode:checkmate](Quantifiedcode) whether your code is free of errors (no login required).

2. The Pull Request should include tests.

3. If the Pull Request adds functionality, also the docs should be updated. Put your new functionality into a function with a docstring, and add the feature to the list in README.rst.

4. The Pull Request should work for Python 2.6, 2.7, and 3.3, and for PyPy. Check [https://travis-ci.org/quantifiedcode/checkmate/pull_requests](https://travis-ci.org/quantifiedcode/checkmate/pull_requests) and make sure that the tests pass for all supported Python versions.

## Tips

To run a subset of tests:

    $ python -m unittest tests.test_checkmate
