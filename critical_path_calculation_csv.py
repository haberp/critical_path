import csv
import re
import datetime
import lxml.etree as ET

#finding the process element ids
def findprocesselementparent(parent_node):
    if parent_node.tag in element_ids_under_process:
        return parent_node.attrib['id']
    else:
        return findprocesselementparent(parent_node.getparent())

bpmn_file_name = 'C:/Users/peter/Downloads/EDM_Consumption_data_collection_at_Nordics_at_2019_11_06.bpmn'
tree = ET.parse(bpmn_file_name)
root = tree.getroot()

parent_map_elements = {c:p for p in root.iter() for c in p}

element_ids_under_process = []
#collecting element ids under the process section
for key, value in parent_map_elements.items():
    if value.tag == '{http://www.omg.org/spec/BPMN/20100524/MODEL}process':
        element_ids_under_process.append(key.tag)

dic = {}
#finding duration values and their process element ids
durations = tree.xpath('//camunda:property', namespaces = root.nsmap)
for _ in durations:
    element_id = findprocesselementparent(_.getparent())
    durationValue = _.attrib['value']
    dic[element_id] = durationValue

print(dic)

colors = tree.xpath('//bpmndi:BPMNEdge', namespaces = root.nsmap)
for _ in colors:
    try:
        color = _.attrib['{http://bpmn.io/schema/bpmn/biocolor/1.0}fill']
    except KeyError:
        pass
    else:
        element_id = _.get('bpmnElement')
        color_dict[element_id] = color

print(color_dict)
    
    #durationValue = _.attrib['value']
    #dic[element_id] = durationValue
