# Release Cycle

## Process

* Update your build tools
```
pip install -U setuptools twine wheel
```
* Update Changelog.md
* Run tox
```
tox
```
* Remove old releases
```
rm dist/*
```
* Create new tag
```
git tag vx.y.z
```
* Checkout to tag
```
git checkout -b vx.y.z
```
* Build releases
```
python setup.py sdist bdist_wheel 
```
* Publish to test.pypi
```
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```
* [Check](https://test.pypi.org/project/stockmanager/) the test project page 

* Test install uploaded release
```
pip3 install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple stockmanager
```
* Upload the official release
```
twine upload dist/*
```
* [Check](https://pypi.org/project/stockmanager/) the public project page 

* Test install uploaded release, in new virenv
```
pip install stockmanager
```
* Draft a release on [Github](https://github.com/wiccy46/stockmanager)

## Further Readings 

* [using test.PyPI](https://packaging.python.org/guides/using-testpypi/)
* [packaging](https://packaging.python.org/tutorials/packaging-projects/)