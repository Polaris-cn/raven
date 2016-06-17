"""
  This Module performs Unit Tests for the mathUtils methods
  It cannot be considered part of the active code but of the regression test system
"""

#For future compatibility with Python 3
from __future__ import division, print_function, unicode_literals, absolute_import
import warnings
warnings.simplefilter('default',DeprecationWarning)

import os,sys
import numpy as np
import xmlUtils
import xml.etree.ElementTree as ET

frameworkDir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(frameworkDir)

print (xmlUtils)

results = {"pass":0,"fail":0}
#type comparison
elemType = type(ET.Element('dummy'))
treeType = type(ET.ElementTree())
#cleanup utilities
toRemove = []

def checkAnswer(comment,value,expected,tol=1e-10,updateResults=True):
  """
    This method is aimed to compare two floats given a certain tolerance
    @ In, comment, string, a comment printed out if it fails
    @ In, value, float, the value to compare
    @ In, expected, float, the expected value
    @ In, tol, float, optional, the tolerance
    @ In, updateResults, bool, optional, if True updates global results
    @ Out, None
  """
  if abs(value - expected) > tol:
    print("checking answer",comment,value,"!=",expected)
    if updateResults: results["fail"] += 1
    return False
  else:
    if updateResults: results["pass"] += 1
    return True

def checkArray(comment,check,expected,tol=1e-10):
  """
    This method is aimed to compare two arrays of floats given a certain tolerance
    @ In, comment, string, a comment printed out if it fails
    @ In, check, list, the value to compare
    @ In, expected, list, the expected value
    @ In, tol, float, optional, the tolerance
    @ Out, None
  """
  same=True
  if len(check) != len(expected):
    same=False
  else:
    for i in range(len(check)):
      same = same*checkAnswer(comment+'[%i]'%i,check[i],expected[i],tol,False)
  if not same:
    print("checking array",comment,"did not match!")
    results['fail']+=1
    return False
  else:
    results['pass']+=1
    return True

def checkType(comment,value,expected,updateResults=True):
  """
    This method compares the data type of two values
    @ In, comment, string, a comment printed out if it fails
    @ In, value, float, the value to compare
    @ In, expected, float, the expected value
    @ In, updateResults, bool, optional, if True updates global results
    @ Out, None
  """
  if type(value) != type(expected):
    print("checking type",comment,value,'|',type(value),"!=",expected,'|',type(expected))
    if updateResults: results["fail"] += 1
    return False
  else:
    if updateResults: results["pass"] += 1
    return True

def attemptFileClear(fName,later):
  """
    Attempts to remove the file.  If not possible, store it in "later".
    @ In, fName, string, name of file to remove
    @ In, later, list, list of files to remove later
    @ Out, later, list, list of files to remove later
  """
  try:
    os.remove(fName)
  except OSError:
    later.append(fName)
  return later

#establish test XML
xmlString = '<root ratr="root_attrib"><child catr1="child attrib 1" catr2="child attrib 2"><cchild ccatr="cc_attrib">cchildtext</cchild></child></root>'
inFileName = 'testXMLInput.xml'
file(inFileName,'w').write(xmlString)
xmlTree = ET.parse(inFileName)
toRemove = attemptFileClear(inFileName,toRemove)

# test prettify
pretty = xmlUtils.prettify(xmlTree)
prettyFileName = 'testXMLPretty.xml'
file(prettyFileName,'w').writelines(pretty)
gold = ''.join(line for line in file(os.path.join(frameworkDir,'gold',prettyFileName),'r'))
test = ''.join(line for line in file(                    prettyFileName ,'r'))
if gold==test:
  results['pass']+=1
  toRemove = attemptFileClear(prettyFileName,toRemove)
else:
  print('ERROR: Test of "pretty" failed!  See',prettyFileName,'vs gold/',prettyFileName)
  results['fail']+=1

# test newNode
### test with tag, text, and multiple attributes
node = xmlUtils.newNode('tagname',text="text",attrib={'atr1':'atr1_text','atr2':'atr2_text'})
okay = True
#type
if type(node)!=elemType:
  okay = False
  print('Test of "newNode" failed!  Returned node was not an xml.etree.ElementTree!  Instead was:',type(node))
#tag
if node.tag!='tagname':
  okay = False
  print('ERROR: Test of "newNode" failed!  Tag should have been "tagname" but instead was "'+node.tag+'".')
#text
if node.text!='text':
  okay = False
  print('ERROR: Test of "newNode" failed!  Text should have been "text" but instead was "'+node.text+'".')
#attributes
if 'atr1' not in node.attrib.keys():
  okay = False
  print('ERROR: Test of "newNode" failed!  Did not find attribute "atr1" in keys:',node.attrib.keys())
else:
  if node.attrib['atr1']!='atr1_text':
    okay = False
    print('ERROR: Test of "newNode" failed! Attribute "atr1" should have been "atr1_text" but was',node.attrib['atr1'])
if 'atr2' not in node.attrib.keys():
  okay = False
  print('ERROR: Test of "newNode" failed!  Did not find attribute "atr2" in keys:',node.attrib.keys())
else:
  if node.attrib['atr2']!='atr2_text':
    okay = False
    print('ERROR: Test of "newNode" failed! Attribute "atr2" should have been "atr2_text" but was',node.attrib['atr2'])
if okay:
  results['pass']+=1
else:
  results['fail']+=1

# test newTree
tree = xmlUtils.newTree('newroot')
okay = True
if type(tree) != treeType:
  okay = False
  print('ERROR: Test of "newTree" failed!  Returned tree was not xml.etree.ElementTree.ElementTree, instead was',type(tree))
elif tree.getroot().tag != 'newroot':
  okay = False
  print('ERROR: Test of "newTree" failed!  Root of new tree should be "newroot" but instead got',tree.getroot().tag)
if okay:
  results['pass']+=1
else:
  results['fail']+=1


# test findPath
###test successful find
found = xmlUtils.findPath(xmlTree.getroot(),'child|cchild')
okay = True
#  type
if type(found)!=elemType:
  okay = False
  print('ERROR: Test of "findPath" failed!  Returned node was not an xml.etree.ElementTree!  Instead was:',type(found))
elif found.tag!='cchild':
  okay = False
  print('ERROR: Test of "findPath" failed!  Returned node tag was not "cchild"!  Instead was:',found.tag)
if okay:
  results['pass']+=1
else:
  results['fail']+=1
###test not found
found = xmlUtils.findPath(xmlTree.getroot(),'child|cchild|notANodeInTheTree')
if found is not None:
  print('ERROR: Test of "findPath" failed!  No element should have been found, but found',found)
  results['fail']+=1
else:
  results['pass']+=1

for f in toRemove:
  if os.path.exists(f):
    try:
      os.remove(f)
    except OSError:
      print('WARNING: In cleaning up, could not remove file',f)



print(results)

sys.exit(results["fail"])
