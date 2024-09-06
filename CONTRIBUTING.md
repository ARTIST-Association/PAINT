# Contributing to PAINT

Welcome to ``PAINT``:sun_with_face:! We're thrilled that you're interested in contributing to our open-source project :fire:.
By participating, you can help improve the project and make it even better :raised_hands:.

## How to Contribute

1. **Fork the Repository:** Click the "Fork" button at the top right corner of this repository's page to create your own copy.

2. **Clone Your Fork:** Clone your forked repository to your local machine using Git :octocat::
   ```bash
   git clone https://github.com/ARTIST-Association/PAINT.git
   ```

3. **Install the Package with Development Options** in a separate virtual environment from the main branch of your repo.
   The commands shown below work on Unix-based systems:
   ```bash
   python3 -m venv <insert/path/to/your/venv>
   source <insert/path/to/your/venv/bin/activate>
   pip install --upgrade pip
   pip install -e ."[dev]"
   ```

4. **Install Pre-Commit Hooks:** This will put a number of [pre-commit](https://pre-commit.com/) hooks for code linting
   and formatting with [Ruff](https://github.com/astral-sh/ruff) as well as type checking with [MyPy](https://www.mypy-lang.org/) into place, ensuring
   PEP-8 conformity and overall good code quality consistently. Run the following command in the root of the project to
   set up the git hook scripts:
   ```bash
   pre-commit install
   ```
   Now `pre-commit` will run automatically on `git commit`!

5. **Create a Branch:** Create a new branch for your contribution. Choose a descriptive name. Depending on what you want
   to work on, prepend either of the following prefixes, `features`, `maintenance`, `bugfix`, or `hotfix`. Example:
   ```bash
   git checkout -b features/your-feature-name
   ```

6. **Make Changes:** Make your desired changes to the codebase. Please stick to the following guidelines:
   * `PAINT` uses [Black](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html)-compatible code style and so should you if you would like to contribute.
   * Please use type hints in all function definitions.
   * Please use American English for all comments and docstrings in the code.

7. **Commit Changes:** Commit your changes with a clear and concise commit message that describes what you have changed.
   Example:
   ```bash
   git commit -m "DESCRIPTION OF YOUR CHANGES"
   ```

8. **Push Changes:** Push your changes to your fork on GitHub:
   ```bash
   git push origin features/your-feature-name
   ```

9. **Rebase Onto Current Main:** Rebase your feature branch onto the current main branch of the original repo.
   This will include any changes that might have been pushed into the main in the meantime and resolve possible conflicts.
   To sync your fork with the original upstream repo, check out [this page](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork)
   or follow the steps below. Note that before you can sync your fork with an upstream repo, you must configure a remote that points to the upstream repository in Git.
   ```
   cd <path/to/your/local/project/fork>
   git fetch upstream
   git checkout main
   git merge upstream/main
   git rebase main features/your-feature-name
   ```
   Alternatively, you can also merge the main branch into your feature branch.

10. **Open a Pull Request:** Go to the [original repository](https://github.com/ARTIST-Association/PAINT.git) and click the "New Pull Request" button. Follow the guidelines in the template to submit your pull request.

## Code of Conduct

Please note that we have a [Code of Conduct](CODE_OF_CONDUCT.md), and we expect all contributors to follow it. Be kind and respectful to one another :blue_heart:.

## Questions or Issues

If you have questions or encounter any issues, please create an issue in the [Issues](https://github.com/ARTIST-Association/PAINT/issues) section of this repository.

Thank you for your contribution :pray:!
