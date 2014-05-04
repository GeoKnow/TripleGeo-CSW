import sys
import os
import socket
import re
import urllib2
import urllib
from lxml import etree
import StringIO
import ConfigParser as configparser

# Globals

config = configparser.ConfigParser()
config.read('config.ini')

# Functions 

def createAll(list):
    s = 'GetRecords.xml'
    namespaces = {'ogc': 'http://www.opengis.net/ogc'}
    with open('GetRecords.xml', 'r') as f:
        obj = etree.parse(f)
        xmlRoot = obj.find(
            './/{http://www.opengis.net/ogc}And', namespaces=namespaces)
        for i in list:
            child = etree.Element(
                "{http://www.opengis.net/ogc}PropertyIsEqualTo")
            xmlRoot.append(child)
            child1 = etree.Element("{http://www.opengis.net/ogc}PropertyName")
            child.append(child1)
            child1.text = i[1] + ':' + i[2]
            child2 = etree.Element("{http://www.opengis.net/ogc}Literal")
            child.append(child2)
            child2.text = '**'

        with open('GetRecords.xml', 'w') as n:
            n.write(
                etree.tostring(obj, xml_declaration=True, encoding='utf-8'))

    # request(s)

##########################################################################
            #Create Post Request#
##########################################################################


def createXmlLike(dictionary, box):
    s = 'GetRecords.xml'
    operCount = 0
    namespaces = {'ogc': 'http://www.opengis.net/ogc'}
    with open('GetRecords.xml', 'r') as f:
        obj = etree.parse(f)
        xmlRoot = obj.find(
            './/{http://www.opengis.net/ogc}And', namespaces=namespaces)
        for k, v in dictionary.items():
            for p in v:
                if '*' in p:
                    child = etree.Element(
                        "{http://www.opengis.net/ogc}PropertyIsLike")
                    child.attrib['wildCard'] = '*'
                    child.attrib['singleChar'] = '_'
                    xmlRoot.append(child)
                    child1 = etree.Element(
                        "{http://www.opengis.net/ogc}PropertyName")
                    child.append(child1)
                    child1.text = k
                    child2 = etree.Element(
                        "{http://www.opengis.net/ogc}Literal")
                    child.append(child2)
                    child2.text = p
                else:
                    if len(v) > 1 and operCount == 0:
                        childRoot = etree.Element(
                            "{http://www.opengis.net/ogc}Or")
                        xmlRoot.append(childRoot)
                        operCount = operCount + 1
                    if operCount == 0:
                        child = etree.Element(
                            "{http://www.opengis.net/ogc}PropertyIsEqualTo")
                        xmlRoot.append(child)
                        child1 = etree.Element(
                            "{http://www.opengis.net/ogc}PropertyName")
                        child.append(child1)
                        child1.text = k
                        child2 = etree.Element(
                            "{http://www.opengis.net/ogc}Literal")
                        child.append(child2)
                        child2.text = p
                    else:
                        child = etree.Element(
                            "{http://www.opengis.net/ogc}PropertyIsEqualTo")
                        childRoot.append(child)
                        child1 = etree.Element(
                            "{http://www.opengis.net/ogc}PropertyName")
                        child.append(child1)
                        child1.text = k
                        child2 = etree.Element(
                            "{http://www.opengis.net/ogc}Literal")
                        child.append(child2)
                        child2.text = p

    if len(box) != 0:
        child = etree.Element("{http://www.opengis.net/ogc}BBOX")
        xmlRoot.append(child)
        childd = etree.Element("{http://www.opengis.net/ogc}PropertyName")
        child.append(childd)
        childd.text = 'ows:BoundingBox'
        childdd = etree.Element("{http://www.opengis.net/gml}Envelope")
        child.append(childdd)
        child1 = etree.Element("{http://www.opengis.net/gml}lowerCorner")
        childdd.append(child1)
        child1.text = box[0]
        child2 = etree.Element("{http://www.opengis.net/gml}upperCorner")
        childdd.append(child2)
        child2.text = box[1]

    with open('GetRecords.xml', 'w') as n:
        n.write(etree.tostring(obj, xml_declaration=True, encoding='utf-8'))

    request(s)

##################################################
#function for transformation XML responses to RDF#
##################################################


def transform(i):
    parser = etree.XMLParser(recover=True)
    dom = etree.parse('out' + str(i) + '.xml', parser)
    xslt = etree.parse('Metadata2RDF.xsl')
    transform = etree.XSLT(xslt)
    newdom = transform(dom)
    rdf = open('out' + str(i) + '.rdf', 'w+')
    rdf.write(etree.tostring(newdom, pretty_print=True))

###########################
#function to POST Requests#
###########################


def request(s):
    csw_endpoints = config.get('main', 'csw_endpoints', '').split()
    i = 1
    for j in csw_endpoints:
        file = open('out' + str(i) + '.xml', 'w')
        url = j
        payload = open(str(s)).read()
        headers = {"Content-type": "application/xml", "Accept": "text/plain"}
        try:
            r = urllib2.Request(url, payload, headers)
            u = urllib2.urlopen(r)
            xml_response = u.read()
            # print xml_response
            if '<gmd:MD_Metadata' in xml_response:
                file = open('out' + str(i) + '.xml', 'w')
                file.write(xml_response)
                transform(i)
                i = i + 1
                print 'Response OK:', j, file
            else:
                print 'Response nothing:', j
        except urllib2.URLError, (err):
            print "URL error(%s)" % (err)
    clear()

###########################################################################
#function to clear temporary Request Files and other. Hit after request() #
###########################################################################


def clear():
    # os.remove(str(s))
    namespaces = {'ogc': 'http://www.opengis.net/ogc'}
    with open('GetRecords.xml', 'r') as f:
        obj = etree.parse(f)
        xmlRoot = obj.find(
            './/{http://www.opengis.net/ogc}And', namespaces=namespaces)
        for elem in xmlRoot:
            # print elem
            xmlRoot.remove(elem)
        with open('GetRecords.xml', 'w') as n:
            n.write(
                etree.tostring(obj, xml_declaration=True, encoding='utf-8'))

#############################################
#Check if filter exists in open file - query#
#############################################


def extract_filter(query_file):
    for i in open(query_file):
        if re.search('filter', i, re.IGNORECASE):
            s = re.search('filter', i, re.IGNORECASE)
            flt = s.group()
            return flt

# Main 

def main(query_file):
    # Todo ...
    pass


####################~START~########################

query_file = sys.argv[1]

list = []
dic = {}
box = []
with open(query_file, 'r') as f:
    for line in f:
        if re.search('([a-z]):([a-z])', line) and 'SELECT' not in line and str(extract_filter(query_file)) not in line:
            if '{' and '}' in line:
                s = line[line.find('{') + 1:line.find('}')]
                rgx1 = re.compile('([\w+\?-]*\w)')
                q = rgx1.findall(s)
                chunks = [q[x:x + 4] for x in xrange(0, len(q), 4)]
                y = [dic.values()]
                for q in chunks:
                    if '?' in q[0] and '?' not in q[3]:
                        k = q[1] + ':' + q[2]
                        if k in dic.keys():
                            dic[k].append(q[3])
                        else:
                            dic[q[1] + ':' + q[2]] = [q[3]]

                    else:
                        list.append(q)

            if '{' and ':' in line and '}' not in line:
                s = line[line.find('{') + 1:line.find('}')]
                rgx1 = re.compile('([\w+\?-]*\w)')
                q = rgx1.findall(s)
                chunks = [q[x:x + 4] for x in xrange(0, len(q), 4)]
                y = [dic.values()]
                for q in chunks:
                    if '?'in q[0] and '?' not in q[3]:
                        k = q[1] + ':' + q[2]
                        if k in dic.keys():
                            dic[k].append(q[3])
                        else:
                            dic[q[1] + ':' + q[2]] = [q[3]]

                    else:
                        list.append(q)

        if re.search('regex', line, re.IGNORECASE):
            s1 = re.search('regex', line, re.IGNORECASE)
            reg = s1.group()
            s = line[line.find(str(reg)):]
            if '&&' in s:
                sf = line[line.find(str(reg)):line.rfind('&&')]
                rgx1 = re.compile('([\w+\^?-]*\w)')
                q = rgx1.findall(sf)
                z = 0
                for j in list:
                    for i in q:
                        if i in j[3]:
                            dic.update(
                                {j[1] + ':' + j[2]: ['*' + q[len(q) - 1] + '*']})
                    z = z + 1
            else:
                sf = line[line.find(str(reg)):line.rfind('}')]
                rgx1 = re.compile('([\w+\^?-]*\w)')
                q = rgx1.findall(sf)
                z = 0
                for j in list:
                    for i in q:
                        if i in j[3]:
                            dic.update(
                                {j[1] + ':' + j[2]: ['*' + q[len(q) - 1] + '*']})
                    z = z + 1

        if re.search('box2d', line, re.IGNORECASE):
            s = re.search('box2d', line, re.IGNORECASE)
            bo = s.group()
            s = line[line.find(bo):]
            box = s.split('(', 1)[1].split(')')[0].split(',')

if len(dic) == 0 and len(box) == 0:
    print 'dictionary empty: nothing to Search.. '
    print 'Searching all available metadata with AnyText..acoording to given predicates.'
    print list
    createAll(list)
else:
    print dic, list, box
    createXmlLike(dic, box)
