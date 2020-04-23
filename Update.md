# How to update package

1. Delete all files in the dist folder.
2. Update the version number in 'nautilus_open_any_terminal/__init__.py'
3. Commit and push changes
4. add release tag
5. `python3 setup.py sdist bdist_wheel`
6. `twine upload dist/*`

