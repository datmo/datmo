# Datmo

## Contributing to Datmo
We encourage community contributions to Datmo. The best place to get started is by running examples 
locally. Once you have it working, contributors can take a shot at improving our documentation. While
our documentation is continually updated with code updates, there is always much room for improvement.
Documentation can be found in the `docs/` directory, in the docstrings for functions in the code, and 
in the `README` file. 

## Pull Request Process
Every contribution, must be a pull request and must have adequate time for review by other committers.

The goal of every pull request is to merge it into the main master code branch. The tasks of reviewing 
a new pull request will be done by the main committers / maintainers of the repository. Here are a few flows for how 
a pull request might progress

1) the PR is not mergeable, in which case either the maintainer or the person who created the branch should then mention they are addressing it and then work on it. If not the case progress to 2
2) the PR is mergeable but requires changes that would need to be done by the person who created the branch / feature, in which case we comment and just keep the thread going -- then it may progress to either 3 or 4
3) the PR is mergeable and is good to go 
4) the PR is mergeable and is almost good to go but requires changes that are quick and can be done by the maintainer -- or by other contributors to the main repo to make it consistent with existing code, in which case we close the current PR, bring the branch into the main repo, and make changes there, then merge

## Code Style Guidelines
Datmo uses [yapf](https://github.com/google/yapf) to autoformat code.

``` bash
pip install yapf==0.20.0
cd <git_root>
yapf -i <python_files changed>
```

Our integration tests will fail if code is not formatted correctly

## Documentation Style Guidelines
Datmo uses [NumPy style documentation](https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt). Please follow these conventions when documenting code, since we use [Sphinx+Napoleon](http://www.sphinx-doc.org/en/stable/ext/napoleon.html) to automatically generate docs on [our Docs page](http://datmo.readthedocs.io/en/latest/)

## Developer Information
You can find more developer information in the [`devtools/` directory](/devtools) including helpful
code snippets and commands you might find helpful in the development process.