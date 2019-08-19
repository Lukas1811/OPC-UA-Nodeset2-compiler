import sys 
import base64
 
from opcua.common.xmlimporter import XmlImporter
from opcua.common.xmlparser import XMLParser

import csv

try:
    inputFile = str(sys.argv[1]) 
    outputFile = str(sys.argv[2]) 
except:
    print("Invalid arguments USAGE : python nodesetParser.py <path to Nodeset2.xml> <Path and name (without extension) for generated files>")
    sys.exit(1)

fieldnames = ["name", "node_id", "type"]

parser = XMLParser(xmlpath=inputFile)

nodes = parser.get_node_datas()
aliases = parser.get_aliases()
namespaces = parser.get_used_namespaces()

def getNodeById(id):
    for node in nodes:
        if node[0] == id:
            return node

def nodeidToId(nodeid):
    node_id = nodeid.split(";")

    if len(node_id) == 2:
        return int(node_id[1].replace("i=",""))
    else:
        return int(node_id[0].replace("i=",""))

def extractIds(nodeset):
    new_nodes = []
    index = 0

    for node in nodes:
        id = nodeidToId(node.nodeid)
        new_nodes.append([int(id) , node])
        
    return new_nodes

def getNodeName(node, prevString=""):
    parentID = nodeidToId(node[1].parent)

    parent = getNodeById(parentID)


    if parent != None:
        if prevString == "":
            return getNodeName(parent, prevString=node[1].displayname)
        else:
            return getNodeName(parent, prevString=node[1].displayname + "_" + prevString)
    else:
        if prevString == "":
            return node[1].displayname
        else:
            return node[1].displayname + "_" + prevString

def nodeSetToCsv(filename):
    with open(filename + ".csv", "w") as csvfile:
        if csvfile == None:
            sys.exit(1)

        writer = csv.DictWriter(csvfile, fieldnames)

        for node in nodes:
            if node[1].displayname not in unwantedTags:
                node_name = getNodeName(node)
                writer.writerow({"name": node_name, "node_id": node[0], "type": node[1].nodetype.replace("UA","")})


def nodeSetToBsd(filename):
    with open(filename + ".bsd", "w") as bsdfile:
        if bsdfile == None:
            sys.exit(1)

        for node in nodes:
            if "TypeDictionary" in node[1].browsename:
                bsdfile.write(node[1].value.decode())

if __name__ == "__main__":
    nodes = extractIds(nodes)
    nodeSetToCsv(outputFile)
    nodeSetToBsd(outputFile)
    pass
