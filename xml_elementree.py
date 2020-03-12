import csv
import re
import datetime
from urllib.request import urlopen
import lxml.etree as ET

CriticalPass = False #True or False
delimiter_char = ";"

#Find the parent element of the element under the process and subprocess
def findprocesselementparent(parent_node):
    if parent_node in element_ids_under_process:
        return(parent_node)
    else:
        parent_of_parent = parent_node.getparent()
        return findprocesselementparent(parent_of_parent)

bpmn_file_name = 'C:/Users/peter/Downloads/BV_-_Bill_Validation_Execution_-_exp.bpmn'
tree = ET.parse(bpmn_file_name)
root = tree.getroot()

parent_map = {c.tag:p.tag for p in root.iter( ) for c in p}
parent_map_elements = {c:p for p in root.iter() for c in p}

elements_under_process = []
#collecting elements under the process section
for key, value in parent_map.items():
    if value == '{http://www.omg.org/spec/BPMN/20100524/MODEL}process':
        elements_under_process.append(key)

#collecting elements under the subprocess section
for key, value in parent_map.items():
    if value == '{http://www.omg.org/spec/BPMN/20100524/MODEL}subProcess':
        elements_under_process.append(key)

element_ids_under_process = []
#collecting element ids under the process section
for key, value in parent_map_elements.items():
    if value.tag == '{http://www.omg.org/spec/BPMN/20100524/MODEL}process':
        element_ids_under_process.append(key)
        
#extend element ids with subprocess element ids
for key, value in parent_map_elements.items():
    if value.tag == '{http://www.omg.org/spec/BPMN/20100524/MODEL}subProcess':
        element_ids_under_process.append(key)
        
#finding duration values and their process element ids
dict_durations = {}
durations = tree.xpath('//camunda:property', namespaces = root.nsmap)
for element_property in durations:
    durationValue = element_property.attrib['value']
    parentTag = findprocesselementparent(element_property.getparent())
    dict_durations[parentTag.get('id')] = durationValue

process_element_ids = {}
#collecting the id and name of the elements under the process
for element in elements_under_process:
    for _ in root.iter(element):
        process_element_ids.update({_.get('id'):[_.get('name')]})
        if process_element_ids[_.get('id')][0] == None:
            process_element_ids.update({_.get('id'):['Missing name']})

if CriticalPass:

    color_dict = {}

    #Process element idk és azok színeinek kigyűjtése a color_dict könyvtárba.{http://www.omg.org/spec/BPMN/20100524/DI}BPMNShape elérhetősége: root[2][0][0].tag
    for task in root.iter('{http://www.omg.org/spec/BPMN/20100524/DI}BPMNShape'):
        task_color = task.get('{http://bpmn.io/schema/bpmn/biocolor/1.0}fill')
        if task_color == 'rgb(187, 222, 251)':
            task_id = task.get('bpmnElement')
            color_dict[task_id] = task_color

    #Connector idk és azok színeinek kigyűjtése a color_dict könyvtárba.
    for task in root.iter('{http://www.omg.org/spec/BPMN/20100524/DI}BPMNEdge'):
        task_color = task.get('{http://bpmn.io/schema/bpmn/biocolor/1.0}fill')
        if task_color == 'rgb(187, 222, 251)':
            task_id = task.get('bpmnElement')
            color_dict[task_id] = task_color

    # if process element id is in the color dictionary selects the the id and name of the process element    
    for task_id, name in process_element_ids.copy().items():
        if task_id not in color_dict.keys():
            del process_element_ids[task_id]

#extending the process element id and name with duration
for key, name in process_element_ids.items():
    if key in dict_durations.keys():
        process_element_ids[key].append(dict_durations[key])
    else:
        process_element_ids[key].append("No duration value")

#Adding key type to the list
for key, value in  process_element_ids.items():
    split = key.split('_')
    process_element_ids[key].append(split[0])

#Creating file name for csv creation
original_file_name = re.findall('([0-9a-zA-Z-_ ]+)\.', bpmn_file_name)
csvFileName = "{}-on-{}-at-{}.csv".format(original_file_name[0], datetime.date.today(), datetime.datetime.now().strftime('%H-%M-%S'))

#writing element id, name and duration to csv
with open (csvFileName, mode='w', newline='\n') as f:
    writer = csv.writer(f, delimiter = delimiter_char, quotechar = '"', quoting=csv.QUOTE_MINIMAL)
    for key in  process_element_ids.keys():
        writer.writerow([process_element_ids[key][1].encode('unicode-escape').decode(), process_element_ids[key][2].encode('unicode-escape').decode(), key, process_element_ids[key][0].encode('unicode-escape').decode()])
    print('CSV file created')
