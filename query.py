#!/usr/bin/env python

import sys
import os
import socket
import re
import urllib2
import urllib
from lxml import etree
from StringIO import StringIO
import tempfile
import logging

import config

# Globals

logger = logging.getLogger(__name__)

# Functions

##########################################################################
# Create Post Request                                                    #
##########################################################################

def createXmlLike(dictionary, box):
    operCount = 0
    emt = ['*', '^', '.', '%']
    doper = ['>','<']
    namespaces = {'ogc': 'http://www.opengis.net/ogc'}
    with open('GetRecords.xml', 'r') as f:
        obj = etree.parse(f)
        xmlRoot = obj.find(
            './/{http://www.opengis.net/ogc}And', namespaces=namespaces)
        for k, v in dictionary.items():
            for p in v:
                if any(b in p for b in doper):
                    a = ''.join([(oper) for oper in doper if oper in p])
                    pdate=p[p.find(str(a))+1:]
                    if a == '<':
                        child = etree.Element(
                            "{http://www.opengis.net/ogc}PropertyIsLessThan")
                        xmlRoot.append(child)
                    if a == '>':
                        child = etree.Element(
                            "{http://www.opengis.net/ogc}PropertyIsGreaterThan")
                        xmlRoot.append(child)

                    child1 = etree.Element(
                        "{http://www.opengis.net/ogc}PropertyName")
                    child.append(child1)
                    child1.text = k
                    child2 = etree.Element(
                        "{http://www.opengis.net/ogc}Literal")
                    child.append(child2)
                    child2.text = pdate

                if any(c in p for c in emt):
                    b=''.join([(wild) for wild in emt if wild in p])
                    child = etree.Element(
                        "{http://www.opengis.net/ogc}PropertyIsLike")
                    child.attrib['wildCard'] = b
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
                    if not any(c in p for c in doper):
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
        child = etree.Element("{http://www.opengis.net/ogc}"+box[2])
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

    
    req = etree.tostring(obj, xml_declaration=True, encoding='utf-8')
    
    outbuf = StringIO()
    request(req, outbuf)

    return outbuf.getvalue()

##################################################
# Transformation of XML responses to RDF         #
##################################################

def transform(temp, outfp):
    temp.seek(0)
    xml = temp.read()
    parser = etree.XMLParser(recover=True)
    dom = etree.fromstring(xml,parser)
    xslt = etree.parse('Metadata2RDF.xsl')
    transformation = etree.XSLT(xslt)
    newdom = transformation(dom)
    outfp.write(etree.tostring(newdom, pretty_print=True))

###########################
# POST Request            #
###########################

def request(payload, outfp):
    csw_endpoints = config.get('main', 'csw_endpoints', '').split()
    for j in csw_endpoints:
        with tempfile.NamedTemporaryFile() as temp:
            url = j
            headers = {"Content-type": "application/xml", "Accept": "text/plain"}
            try:
                r = urllib2.Request(url, payload, headers)
                u = urllib2.urlopen(r)
                xml_response = u.read()
                if '<gmd:MD_Metadata' in xml_response:
                    temp.write(xml_response)
                    transform(temp, outfp)
                    logger.info('Response OK: ' +j)
                else:
                    logger.info('Response NONE: ' +j)
            except urllib2.URLError as ex:
                logger.error('Failed to complete rrquest: %s', str(ex))
    return    

#########################################################
#Check if filter exists in open file AND enumerate lines
#Create a Valid RDF
#########################################################
def validation(result):
    buf = StringIO()
    with tempfile.TemporaryFile() as tp:
        tp.write(result)
        tp.seek(0)
        line = tp.readlines()
        buf.write(line[0])
        for l in line:
            if not 'rdf:RDF' in l:
                buf.write(l)
        buf.write(line[-1])

        return buf.getvalue() 


def extract_filter(query_file):
    for i in open(query_file):
        if re.search('filter', i, re.IGNORECASE):
            s = re.search('filter', i, re.IGNORECASE)
            flt = s.group()
            return flt

def enumerate_file(query_file):
    for x, line in enumerate(open(query_file)):
        if re.search('where', line, re.IGNORECASE):
            return x


# Main

def invoke(query_file):
    result = None
    lst = []
    dic = {}
    box = []
    with open(query_file, 'r') as f:
        a = enumerate_file(query_file)
        for line in f.readlines()[a:]:
            if re.search('(dc):([A-Za-z])', line) and str(extract_filter(query_file)) not in line:
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
                            lst.append(q)

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
                            lst.append(q)

            if re.search('regex', line, re.IGNORECASE):
                operators = ['&&', '||']
                s1 = re.search('regex', line, re.IGNORECASE)
                reg = s1.group()
                s = line[line.find(str(reg)):]
                if any(l in s for l in operators):
                    a = ''.join([(oper) for oper in operators if oper in s])
                else:
                    a = '}'
                sf = line[line.find(str(reg)):line.rfind(str(a))]
                rgx1 = re.compile('([\w+\*^%?-]*\w)')
                q = rgx1.findall(sf)
                for j in lst:
                    for i in q:
                        if i in j[3]:
                            dic.update(
                                {j[1] + ':' + j[2]: [q[len(q) - 1] ]})


            if re.search('box2d', line, re.IGNORECASE):
                s = re.search('box2d', line, re.IGNORECASE)
                bo = s.group()
                s = line[line.find(bo):]
                box = s.split('(', 1)[1].split(')')[0].split(',')
                spatial = ['Equals','Crosses','Contains','Within','Intersects','Touches','Disjoint','Overlaps']
                FilCap =''.join([(capa) for capa in spatial if capa in line])
                if FilCap:
                    box.append(FilCap)
                else:
                    box.append('BBOX')

            if re.search(r'(\d+-\d+-\d+)', line):
                match = re.search(r'(\d+-\d+-\d+)', line)
                date = match.group()
                dts=['date','modified']
                for iter in lst:
                    if any(b in iter for b in dts):
                        dl = line[line.rfind(iter[3]):line.find(date)-1]
                        if '>' in dl:
                            dic[iter[1] + ':' + iter[2]] = ['>' + date]
                        if '<' in dl:
                            dic[iter[1] + ':' + iter[2]] = ['<' + date]


    if dic or box:
        result = createXmlLike(dic, box)
    
    return result

# Start ...

if __name__ == '__main__':
    query_file = sys.argv[1]
    result = invoke(query_file)
    if result:
        ValidRDF = validation(result)
        print ValidRDF
