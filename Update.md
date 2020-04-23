# How to update package

1. Delete all files in the dist folder.
2. Update the version number in 'nautilus_open_any_terminal/open_any_terminal_extension.py'
3. `python3 setup.py sdist bdist_wheel`
4. `twine upload dist/*`
