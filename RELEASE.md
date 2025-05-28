# Releasing a new version of `PAINT`

The current workflow for releasing a new version of `PAINT` is as follows:
1. Make sure the main branch is up-to-date and contains the version of the software that it is to be released.
2. On the main branch, update the version number in `pyproject.toml`. We use semantic versioning.
3. Rebase the ``release-test`` branch onto the current main branch.
4. Push the ``release-test`` branch. This triggers a GitHub :octocat: action that will publish `PAINT` to TestPyPi and
automatically verify that the TestPyPi version of ``PAINT`` works as planned by running all tests.
5. If the TestPyPi release worked as desired, rebase the ``release`` branch onto current main branch.
6. Make GitHub :octocat: release from the current main, including the corresponding version tag.
7. This will trigger an automatic Zenodo archive of the repository. Once this archive is available, update the Zenodo badge in the README to the latest version.
8. Push release branch. This will trigger a GitHub :octocat: action publishing the new release on PyPI.
