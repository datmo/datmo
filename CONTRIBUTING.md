# Datmo

Guidelines for contributors coming soon. 

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