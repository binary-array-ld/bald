from __future__ import print_function

import argparse
import jinja2
import json
import netCDF4
import numpy
import os
import re
import sys


def parseArgs(args):
    '''
    Parse the command line arguments into a dictionary object.
    
    args [in] A list of command line arguments.
    returns   A dictionary of the parse results.
    '''
    
    parser = argparse.ArgumentParser(description = 'Generate web-linked CDL (without data) from a netCDF-LD file as HTML.',
                                     epilog = 'If no output file is specified, the output will be written to the file ncldDump.html in the current folder.')
    
    parser.add_argument('-a',        metavar = '<alias file>', default = None,
                        dest = 'aliasFile', help = 'A JSON file containing alias definitions.')
    parser.add_argument('-o',        metavar = '<output file>', default = 'ncldDump.html',
                        dest = 'outputFile', help = 'The file to write the output to.')
    parser.add_argument('inputFile', metavar = '<input file>',   help = 'A netCDF-LD file.')
    
    parsedArgs = parser.parse_args(args)
    
    assert os.access(parsedArgs.inputFile, os.R_OK), 'Unable to read file ' + parsedArgs.inputFile
    
    if parsedArgs.aliasFile is not None:
        assert os.access(parsedArgs.aliasFile, os.R_OK), 'Unable to read file ' + parsedArgs.aliasFile
    
    argDict = vars(parsedArgs)
    
    return argDict


def parseDtype(dtype):
    '''
    Return a string representing the data type in the dtype argument.
    
    dtype [in] A dtype object.
    returns    A string.
    '''
    
    # Get the basic two character type string for the type. Remove any
    # byte-order information or other extraneous characters.
    #
    theType = dtype.str.strip('><=#')
    
    # Map the type. If the type is not found, return '?'.
    #
    result = '?'
    
    if   'i1' == theType:
        result = 'byte'
    elif 'u1' == theType:
        result = 'ubyte'
    elif 'i2' == theType:
        result = 'short'
    elif 'u2' == theType:
        result = 'ushort'
    elif 'i4' == theType:
        result = 'int'
    elif 'u4' == theType:
        result = 'uint'
    elif 'f4' == theType:
        result = 'float'
    elif 'i8' == theType:
        result = 'int64'
    elif 'u8' == theType:
        result = 'uint64'
    elif 'f8' == theType:
        result = 'double'
    elif 'S1'  == theType:
        result = 'char'
    elif 'S'  == theType:
        result = 'string'
    elif 'U'  == theType:
        result = 'string'
    
    # Return the result.
    #
    return result


def parseType(obj):
    '''
    Return a string representing the data type of the obj argument.
    
    dtype [in] A dtype object.
    returns    A string.
    '''
    
    # Map the type. If the type is not found, return '?'.
    #
    result = '?'
    
    if   True == isinstance(obj, unicode):
        result = ''
    elif True == isinstance(obj, str):
        result = ''
    elif True == isinstance(obj, numpy.int8):
        result = 'b'
    elif True == isinstance(obj, numpy.uint8):
        result = 'ub'
    elif True == isinstance(obj, numpy.int16):
        result = 's'
    elif True == isinstance(obj, numpy.uint16):
        result = 'us'
    elif True == isinstance(obj, numpy.int32):
        result = ''
    elif True == isinstance(obj, numpy.uint32):
        result = 'u'
    elif True == isinstance(obj, numpy.int64):
        result = 'll'
    elif True == isinstance(obj, numpy.uint64):
        result = 'ull'
    elif True == isinstance(obj, numpy.float32):
        result = 'f'
    elif True == isinstance(obj, numpy.float64):
        result = ''
    elif True == isinstance(obj, numpy.ndarray):
        result = parseType(obj[0])
    
    # Return the result.
    #
    return result


def convertToStringHook(item, ignoreDicts = False):
    '''
    This function is passed to the json load function as an object hook. It
    converts any unicode strings into ASCII strings.
    
    item        [in] An item passed in for processing.
    ignoreDicts [in] If this is set to True ignore any dict objects passed in.
    returns          Items with any unicode strings converted to ASCII.
    '''
    
    # If this is a unicode string, convert it. If this is a list, convert any
    # contained unicode strings. If this is a dict and it hasn't been converted
    # already, convert any contained unicode strings. Otherwise, leave the item
    # alone.
    #
    if isinstance(item, unicode):
        result = item.encode('utf-8')
    elif isinstance(item, list):
        result = [ convertToStringHook(element, True) for element in item ]
    elif isinstance(item, dict) and not ignoreDicts:
        result = { convertToStringHook(key, True) : convertToStringHook(value, True) for key, value in item.iteritems() }
    else:
        result = item
    
    # Return the possibly converted item.
    #
    return result


def loadAliasDict(aliasFilePath):
    '''
    Load an alias dictionary from a JSON file. This is a temporary workaround
    until it is decided how to store the information in a netCDF-LD file.  The
    alias dictionary is a mapping of URIs to context prefixes and words.  The
    words will be found in variable and attribute names, and in words found in
    specified attribute values. If the file path is None, create a stubbed-out
    dictionary and return it.
    
    aliasFilePath [in] The path to the JSON file containing the alias
                       definitions.
    returns            The loaded dictionary.
    '''
    
    # If the file path is None, create a stubbed-out dictionary.
    #
    if aliasFilePath is None:
        aliasDict = { 'contexts' : {}, 'names' : {}, 'values' : {} }
    else:
        # Open the file to parse.
        #
        aliasFile = open(aliasFilePath)
        
        # Parse the contained JSON.
        #
        aliasDict = json.load(aliasFile, object_hook = convertToStringHook)
    
    # Return the dictionary.
    #
    return aliasDict


def makeHotLink(word, pattern):
    '''
    Create an <a> hot-link string from the word and pattern.
    
    word    [in] The word to build the hot-link around.
    pattern [in] The URL pattern to reference.
    returns      An <a> hot-link string.
    '''
    
    # Insert the word into any replaceable part in the pattern.
    #
    theURL = pattern.format(word)
    
    # Create the hot-link string. Make it open a new tab when dereferenced if
    # the URL is not relative to the current document.
    #
    if '#' != theURL[0]:
        hotLink = '<a href="{}" target="_blank">{}</a>'.format(theURL, word)
    else:
        hotLink = '<a href="{}">{}</a>'.format(theURL, word)
    
    # Return the hot-link string.
    #
    return hotLink


def parseAttributes(ncObj, aliasDict):
    '''
    Build a list of dictionaries for each netCDF attribute on the object.
    
    ncObj [in] A netCDF object with attributes.
    returns    A list of dictionaries for each attribute.
    '''
    
    # Create the attribute list.
    #
    attrList = []
    
    # Fill the list with dictionaries describing each attribute.
    #
    for attrName in ncObj.ncattrs():
        attrValue = ncObj.getncattr(attrName)
        attrType  = parseType(attrValue)
        
        # If the value is an array, create a list for the contents.
        #
        if True == isinstance(attrValue, numpy.ndarray):
            valueList = []
            
            for value in attrValue:
                # If the attribute name and value are in the alias dictionary
                # values section, get a hot-link string for it.
                #
                if attrName in aliasDict['values']:
                    subDict = aliasDict['values'][attrName]
                    
                    # If the key '*' is present in the sub-dictionary, get the
                    # item, otherwise get the item keyed by the value.
                    #
                    if '*' in subDict:
                        pattern = subDict['*']
                    else:
                        pattern = subDict[value]
                    
                    value = makeHotLink(value, pattern)
                    
                # If the value is a string, wrap it in '"' characters.
                #
                if True == isinstance(value, str) or True == isinstance(value, unicode):
                    valueList.append('"' + str(value) + '"')
                else:
                    valueList.append(str(value))
            
            attrValue = valueList
        else:
            # If the attribute name and value are in the alias dictionary
            # values section, get a hot-link string for it.
            #
            if attrName in aliasDict['values']:
                subDict = aliasDict['values'][attrName]
                
                # If the key '*' is present in the sub-dictionary, get the
                # item, otherwise get the item keyed by the value.
                #
                if '*' in subDict:
                    pattern = subDict['*']
                else:
                    pattern = subDict[attrValue]
                
                attrValue = makeHotLink(attrValue, pattern)
                
            # If the value is a string, wrap it in '"' characters.
            #
            if True == isinstance(attrValue, str) or True == isinstance(attrValue, unicode):
                attrValue = '"' + str(attrValue) + '"'
            else:
                attrValue = str(attrValue)
        
        # If the attribute name is in the alias dictionary names section, get a
        # hot-link string for it.
        #
        if attrName in aliasDict['names']:
            pattern = aliasDict['names'][attrName]
            
            attrName = makeHotLink(attrName, pattern)
        
        attrList.append({'name' : attrName, 'value' : attrValue, 'type' : attrType})
    
    # Return the list.
    #
    return attrList


def parseNcObj(ncObj, aliasDict):
    '''
    Build dimension, variable, and attribute lists for the object.
    
    ncObj [in] The netCDF4 object to parse.
    returns    A nested set of dictionaries and lists describing the object
               contents.
    '''
    
    # Create the top-level dictionary.
    #
    dataDict = {}
    
    # If there are any dimensions, add and populate a dimensions element.
    #
    dimList = []
    
    try:
        for dimName, dimObj in ncObj.dimensions.iteritems():
            dimEntry = {'name' : dimName }
            
            if True == dimObj.isunlimited():
                dimEntry['value']   = 'UNLIMITED'
                dimEntry['comment'] = str(dimObj.size) + ' currently'
            else:
                dimEntry['value'] = str(dimObj.size)
            
            dimList.append(dimEntry)
    except:
        pass
    
    if 0 < len(dimList):
        dataDict['dimensions'] = dimList
    
    # If there are any variables, add and populate a variables element.
    #
    varList = []
    
    try:
        for varName, varObj in ncObj.variables.iteritems():
            varType = parseDtype(varObj.dtype)
            
            varEntry = {'name' : varName, 'type' : varType}
            
            dimList = []
            
            for dimName in varObj.dimensions:
                dimSize = ncObj.dimensions[dimName].size
                
                dimList.append('{}={}'.format(dimName, dimSize))
            
            if 0 < len(dimList):
                varEntry['dimensions'] = dimList

            # If the variable name is in the alias dictionary names section,
            # get a hot-link string for it and add it to the entry for the
            # variable. If not, just use the name.
            #
            hotLink = varName
            
            if varName in aliasDict['names']:
                pattern = aliasDict['names'][varName]
                
                hotLink = makeHotLink(varName, pattern)
            
            varEntry['hotLink'] = hotLink
            
            # If there are any attributes add and populate an attributes
            # element.
            #
            attrList = parseAttributes(varObj, aliasDict)
            
            if 0 < len(attrList):
                varEntry['attributes'] = attrList

            varList.append(varEntry)
    except:
        pass
    
    if 0 < len(varList):
        dataDict['variables'] = varList
    
    # If there are any group-level attributes, add and populate an attributes
    # element.
    #
    attrList = parseAttributes(ncObj, aliasDict)
    
    if 0 < len(attrList):
        dataDict['attributes'] = attrList
    
    # Return the dictionary.
    #
    return dataDict


def ncldDump(inputFile, aliasFile, outputFile):
    '''
    Generate an HTML page from a netCDF-LD file. The page will contain CDL
    describing the structure and contents of the file (without data values),
    similar to the output of ncdump. Any elements that have associated linked
    data will be presented as hot links that will open a new browser tab that
    shows the linked contents.
    
    inputFile  [in] The netCDF-LD file to parse and display.
    aliasFile  [in] A JSON file with alias definitions. If the value is None,
                    no aliases are defined.
    outputFile [in] The output file to write to.
    '''
    
    # Load the alias dictionary.
    #
    aliasDict = loadAliasDict(aliasFile)
    
    # Get a netCDF4 dataset object from the input file and open it.
    #
    ncObj = netCDF4.Dataset(inputFile, 'r')
    
    # Parse the contents of the netCDF file into a dictionary.
    #
    ncDict = parseNcObj(ncObj, aliasDict)
    
    # Add a filePath entry.
    #
    ncDict['filePath'] = inputFile
    
    # Create a jinja environment and template object.
    #
    envObj = jinja2.Environment(loader = jinja2.FileSystemLoader('./'))
    
    templateObj = envObj.get_template('ncldDump_template.html')
    
    # Render the template with the contents of the dictionary.
    #
    result = templateObj.render(**ncDict)
    
    # Open the output file and write the rendered template into it.
    #
    outObj = open(outputFile, 'w')
    
    outObj.write(result)
    
    outObj.close()


if __name__ == '__main__':
    try:
        argDict = parseArgs(sys.argv[1:])
    
        ncldDump(**argDict)
    except Exception as exc:
        print(exc)
        
        if 'pdb' not in sys.modules:
            sys.exit(1)
