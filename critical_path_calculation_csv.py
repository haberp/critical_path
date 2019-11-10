import csv
import re
import datetime
from urllib.request import urlopen
import lxml.etree as ET

bpmn_file_name = 'C:/Users/vajda/Downloads/EDM - Consumption data collection at Nordics -at- 2019-11-06.bpmn'
tree = ET.parse(bpmn_file_name)
root = tree.getroot()

#process = tree.xpath('//bpmn:process', namespaces = root.nsmap)
#print(root.find('bpmn:process', root.nsmap))

delimiter_char = ";"

parent_map = {c.tag:p.tag for p in root.iter( ) for c in p}

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

elements_under_process = []

#collecting elements under the process section
for key, value in parent_map.items():
    if value == '{http://www.omg.org/spec/BPMN/20100524/MODEL}process':
        elements_under_process.append(key)

process_element_ids = {}

#collecting the id and name of the elements under the process
for element in elements_under_process:
    for _ in root.iter(element):
        process_element_ids[_.get('id')] = _.get('name')

# if process element id is in the color dictionary selects the the id and name of the process element
list_of_elements_on_critical_path = {}
for task_id, name in process_element_ids.items():
    if task_id in color_dict.keys():
        list_of_elements_on_critical_path[task_id] = [name]

#getting duration and task id of process elements
list_of_elements_with_duration = {}
for element in elements_under_process:
    for task in root.iter(element):
        try:
            duration = task[0][0][0].attrib['value']
        except IndexError:
            pass
        else:
            task_id = task.get('id')
            list_of_elements_with_duration[task_id] = duration

#extending the process element id and name with duration
for key, duration in list_of_elements_with_duration.items():
    if key in list_of_elements_on_critical_path.keys():
        list_of_elements_on_critical_path[key].append(duration)

deletable_keys = set()

for key, value in list_of_elements_on_critical_path.items():
    if len(value) < 2:
        deletable_keys.add(key)
    
for key in deletable_keys:    
    del list_of_elements_on_critical_path[key]

#Creating file name for csv creation
original_file_name = re.findall('([0-9a-zA-Z- ]+)\.', bpmn_file_name)
csvFileName = "{}-on-{}-at-{}.csv".format(original_file_name[0], datetime.date.today(), datetime.datetime.now().strftime('%H-%M-%S'))

#Adding key type to the list
for key, value in  list_of_elements_on_critical_path.items():
    split = key.split('_')
    list_of_elements_on_critical_path[key].append(split[0])

#writing element id, name and duration to csv

with open (csvFileName, mode='w', newline='\n') as f:
    writer = csv.writer(f, delimiter = delimiter_char, quotechar = '"', quoting=csv.QUOTE_MINIMAL)
    for key in  list_of_elements_on_critical_path.keys():
        writer.writerow([list_of_elements_on_critical_path[key][1].encode('unicode-escape').decode(), list_of_elements_on_critical_path[key][2].encode('unicode-escape').decode(), key, list_of_elements_on_critical_path[key][0].encode('unicode-escape').decode()])
    print('CSV file created')
