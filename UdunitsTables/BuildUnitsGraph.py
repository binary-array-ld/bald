from __future__ import print_function
from neo4jrestclient.client import GraphDatabase, Node, Relationship

import re
import sys
import xml.etree.ElementTree as ETree


def createNode(dB, label = None, properties = None):
    if label is None and properties is None:
        raise Exception(args = ('ERROR: createNode() called with both label and properties arguments = None.',))
    
    if label is not None and type(label) is not str and type(label) is not unicode:
        raise Exception(args = ('ERROR: createNode() called with a label argument that is not a str or unicode type.',))
    
    if type(properties) is not dict:
        raise Exception(args = ('ERROR: createNode() called with a properties argument that is not a dict type.',))
    
    query = 'CREATE (n'
    
    if label is not None:
        query += ':' + label
    
    if properties is not None and 0 < len(properties):
        query += ' {'
        
        for prop in properties:
            query += prop + ' : {' + prop + '}, '
        
        query = query[:-2] + '}'
    
    query += ') return n'
    
    node = dB.query(query, params = properties, returns = (Node,))[0][0]
    
    return node


def mergeNode(dB, label = None, properties = None):
    if label is None and properties is None:
        raise Exception(args = ('ERROR: mergeNode() called with both label and properties arguments = None.',))
    
    if label is not None and type(label) is not str and type(label) is not unicode:
        raise Exception(args = ('ERROR: mergeNode() called with a label argument that is not a str or unicode type.',))
    
    if type(properties) is not dict:
        raise Exception(args = ('ERROR: mergeNode() called with a properties argument that is not a dict type.',))
    
    query = 'MERGE (n'
    
    if label is not None:
        query += ':' + label
    
    if properties is not None and 0 < len(properties):
        query += ' {'
        
        for prop in properties:
            query += prop + ' : {' + prop + '}, '
        
        query = query[:-2] + '}'
    
    query += ') return n'
    
    try:
        node = dB.query(query, params = properties, returns = (Node,))[0][0]
    except:
        raise Exception(args = ('ERROR: dB.query failed in mergeNode.',))
    
    return node


def mergeRelationship(dB, fromNode, relType, toNode, properties = None):
    if relType is None:
        raise Exception(args = ('ERROR: mergeRelationship() called with a relType argument of None.',))
    
    if type(relType) is not str and type(relType) is not unicode:
        raise Exception(args = ('ERROR: mergeRelationship() called with a relType argument that is not a str or unicode type.',))
    
    if properties is not None and type(properties) is not dict:
        raise Exception(args = ('ERROR: mergeRelationship() called with a properties argument that is not a dict type.',))
    
    query = 'START a = node({_from}), b = node({_to}) MERGE (a)-[r:' + relType
    
    if properties is not None and 0 < len(properties):
        query += ' {'
        for property in properties:
            query += property + ':{' + property + '}, '
        
        query = query[0:-2] + '}'
    
    query += ']->(b) RETURN r'
    
    if properties is not None:
        params = dict(properties)
    else:
        params = dict()
    
    params['_from'] = fromNode.id
    params['_to']   = toNode.id
    
    relationship = dB.query(query, params = params, returns = (Relationship,))[0][0]
    
    return relationship


def getNames(nameElement, noPlural = False):
    theName = nameElement.find('./singular').text
    
    pluralElement   = nameElement.find('./plural')
    noPluralElement = nameElement.find('./noplural')
    
    if noPluralElement is not None or noPlural == True:
        thePlural = None
    elif pluralElement is not None:
        thePlural = pluralElement.text
    else:
        if re.search('ch$|sh$|s$|x$', theName) is not None:
            thePlural = theName + 'es'
        elif re.search('[^aeiou]y$', theName) is not None:
            thePlural = theName[:-1] + 'ies'
        else:
            thePlural = theName + 's'
    
    commentElements = list()

    commentElements.extend(nameElement.findall('[@comment]'))
    commentElements.extend(nameElement.findall('.*[@comment]'))
    
    theComments = list()
    
    for element in commentElements:
        theComments.append(element.attrib['comment'])
    
    return (theName, thePlural, theComments)


def mergeNameNode(dB, nameElement, noPlural = False):
    if nameElement is None:
        raise Exception(args = ('ERROR: The nameElement argument is None.',))
    
    properties = {}
    
    theName, thePlural, theComments = getNames(nameElement, noPlural)
    
    properties['name'] = theName
    
    if thePlural is not None:
        properties['plural'] = thePlural
    
    if len(theComments) > 0:
        properties['comments'] = theComments
    
    unitNode = mergeNode(dB, 'UnitName', properties)
    
    return unitNode


def addNamesAndSymbols(dB, unitNode, parentElement):
    nameElements         = parentElement.findall('./name')
    noPluralElement      = parentElement.find('./noplural')
    symbolElements       = parentElement.findall('./symbol')
    
    noPlural = False
    
    if noPluralElement is not None:
        noPlural = True
    
    for nameElement in nameElements:
        nameNode = mergeNameNode(dB, nameElement, noPlural)
        
        mergeRelationship(dB, nameNode, 'NAME_FOR', unitNode)
    
    for symbolElement in symbolElements:
        properties = dict()
        
        properties['name'] = symbolElement.text
        
        if 'comment' in symbolElement.attrib:
            properties['comment'] = symbolElement.attrib['comment']
        
        symbolNode = mergeNode(dB, 'UnitSymbol', properties)
        
        mergeRelationship(dB, symbolNode, 'SYMBOL_FOR', unitNode)


def addUnit(dB, unitElement):
    aliasesElement       = unitElement.find('./aliases')
    baseElement          = unitElement.find('./base')
    defElement           = unitElement.find('./def')
    dimensionlessElement = unitElement.find('./dimensionless')
    nameElement          = unitElement.find('./name')
    definitionElement    = unitElement.find('./definition')
    commentElement       = unitElement.find('./comment')
    
    unitNode   = None
    properties = dict()
    
    if definitionElement is not None and definitionElement.text is not None:
        properties['definition'] = definitionElement.text
    
    if commentElement is not None:
        properties['comment'] = commentElement.text
    
    if defElement is not None:
        properties['formula'] = defElement.text
    elif baseElement is not None or dimensionlessElement is not None:
        if nameElement is None:
            raise Exception(args = ('ERROR: base or dimesionless unit does not have a name element.',))
        
        nameText = nameElement.find('./singular').text
        
        if baseElement is not None:
            properties['formula']       = 'Base SI unit'
            properties['canonicalName'] = nameText
        elif dimensionlessElement is not None:
            properties['formula']       = 'Dimensionless quantity'
            properties['canonicalName'] = nameText
    else:
        raise Exception(args = ('ERROR: unit does not have a def, base, or dimensionless element.',))
    
    unitNode = mergeNode(dB, 'Unit', properties)
    
    if nameElement is not None:
        addNamesAndSymbols(dB, unitNode, unitElement)
    
    if aliasesElement is not None:
        addNamesAndSymbols(dB, unitNode, aliasesElement)


def addPrefix(dB, prefixElement):
    valueElement          = prefixElement.find('./value')
    nameElement           = prefixElement.find('./name')
    symbolElements        = prefixElement.findall('./symbol')
    
    if valueElement is None or nameElement is None or symbolElements is None or 0 == len(symbolElements):
        raise Exception(args = ('ERROR: Prefix element is incomplete.',))
    
    prefixNode = mergeNode(dB, 'Prefix', {'name' : nameElement.text, 'value' : valueElement.text})
    
    for symbolElement in symbolElements:
        properties = dict()
        
        properties['name'] = symbolElement.text
        
        if 'comment' in symbolElement.attrib:
            properties['comment'] = symbolElement.attrib['comment']
        
        symbolNode = mergeNode(dB, 'PrefixSymbol', properties)
        
        mergeRelationship(dB, symbolNode, 'SYMBOL_FOR', prefixNode)


def addUnits(dB, file):
    eTree       = ETree.parse(file)
    rootElement = eTree.getroot()
    
    unitElements = rootElement.findall('./unit')
    
    for unitElement in unitElements:
        addUnit(dB, unitElement)
    
    prefixElements = rootElement.findall('./prefix')
    
    for prefixElement in prefixElements:
        addPrefix(dB, prefixElement)


def parseFormulas(dB):
    iter = dB.labels.get('UnitName').all()
    
    nameDict = dict()
    
    for name in iter:
        nameDict[name['name']] = name
        
        try:
            nameDict[name['plural']] = name
        except:
            pass
    
    iter = dB.labels.get('UnitSymbol').all()
    
    for symbol in iter:
        nameDict[symbol['name']] = symbol
    
    iter = dB.labels.get('Prefix').all()
    
    prefixList = list()
    
    for prefix in iter:
        prefixList.append(prefix['name'])
    
    iter = dB.labels.get('PrefixSymbol').all()
    
    for symbol in iter:
        prefixList.append(symbol['name'])
    
    partsRegex  = re.compile('[. @/)^(+-]')
    ignoreRegex = re.compile('\d+e?\d*$|lg$|re$')
    trailRegex  = re.compile('\d+$')
    
    for unit in dB.labels.get('Unit').all():
        referenceList = list()
        sourceList    = list()
        
        theFormula = unit['formula']
        
        if 'Base SI unit' == theFormula or 'Dimensionless quantity' == theFormula:
            continue
        
        parts = partsRegex.split(theFormula)
        
        for part in parts:
            if '' == part:
                continue
            
            if ignoreRegex.match(part) is not None:
                continue
            
            part = trailRegex.sub('', part)
            
            if '' == part:
                continue
            
            fullName = part

            if part not in nameDict:
                part = None
                
                for prefix in prefixList:
                    aMatch = re.match(prefix + '(.*)$', fullName)
                    
                    if aMatch:
                        base = aMatch.group(1)
                        
                        if base in nameDict:
                            part = base
                            
                            break
            
            if part is not None:
                referenceList.append(part)
                sourceList.append(fullName)
                
                mergeRelationship(dB, unit, 'REFERENCES', nameDict[part], properties = {'as' : fullName})
                
        if 0 == len(referenceList):
            continue
        
        unit['references'] = referenceList
        unit['sources']    = sourceList


def main():
    dB = GraphDatabase('http://localhost:7474/db/data/') 
    
    for file in sys.argv[1:]:
        addUnits(dB, file)
    
    parseFormulas(dB)


if __name__ == '__main__':
    main() 
