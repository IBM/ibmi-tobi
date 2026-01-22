# Testing TOBi

## Doctest 
makei/utils.py can be tested via doctest
Requires PYTHONPATH being set to the ibmi-tobi project root so that the 'makei' module is recognized. 
```
export PYTHONPATH=<tobi project root>/src
python makei/utils.py -v
```

## VS Code Test Explorer
makei/tests contains tests that can be run through VS Code Test Explorer extension

## Running makei
1. Use the https://github.com/edmundreinhardt/tobi-example and do a `makei b -e <yourlib>` into an empty directory
2. Use the https://github.com/worksofliam/company_system and do a `makei b -e <yourlib>` into an empty directory
( tests with an empty iproj.json includePath)

3. Touch one file and do a makei again and see only those affected files build
4. Touch one file and do a `makei c -f <sourcefile>` and see only the target built
5. Touch one file in a directory and do a `makei c -f <dirname>` to see only that file built
