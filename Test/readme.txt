#To run all unit tests, do (from main directory):
#py -m unittest

#To run some subset of the tests that match a string, do:
#py -m unittest -k stringToMatch
#For example, if you want to run just the method "testRunningTwice", you could do
#py -m unittest -k testRunningTwice
#Or, if you wanted to run all methods for Elf, you could do
#py -m unittest -k testElf*

#To run just one test class instead of all of them:
#py -m unittest Test.<TestClassName>
#Ex: py -m unittest Test.TestRESTEndpoints

#You can also test and debug tests using unittest in VSCode using the Python extension
#and clicking on the beaker icon 
#See https://code.visualstudio.com/docs/python/testing