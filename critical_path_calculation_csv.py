#This program collects the process elements from a bpmn file with their name, type and duration and exports them to csv file
#Creator: Peter Haber
#Version: 1.0

import csv
import re
import datetime
from urllib.request import urlopen
import lxml.etree as ET
import config

def find_process_element_parent(parent_node):
    #Find the parent element of the element under the process and subprocess
    if parent_node in element_ids_under_process:
        return(parent_node)
    else:
        parent_of_parent = parent_node.getparent()
        return find_process_element_parent(parent_of_parent)

def collect_elemets_under_process():
    global elements_under_process
    #Collecting elements under the process section
    for key, value in parent_map.items():
        if value in config.process_elements:
            elements_under_process.append(key)


def collect_elemet_ids_under_process():
    global element_ids_under_process
    #Collecting element ids under the process section
    for key, value in parent_map_elements.items():
        if value.tag in config.process_elements:
         element_ids_under_process.append(key)
            
def collect_elemets_with_duration():
    #Finding duration values and their process element ids
    global dict_durations
    durations = tree.xpath('//camunda:property', namespaces = root.nsmap)
    for element_property in durations:
        durationValue = element_property.attrib['value']
        parentTag = find_process_element_parent(element_property.getparent())
        dict_durations[parentTag.get('id')] = durationValue

def collect_element_id_and_name():
    #Collecting the id and name of the elements under the process
    global process_element_ids
    for element in elements_under_process:
        for _ in root.iter(element):
            process_element_ids.update({_.get('id'):[_.get('name')]})
            if process_element_ids[_.get('id')][0] == None:
                process_element_ids.update({_.get('id'):['Missing name']})

def collect_shape_element_id_and_colors():
    #Collect Shape element ids and colors from color_dict dictionary
    global color_dict
    for task in root.iter('{http://www.omg.org/spec/BPMN/20100524/DI}BPMNShape'):
        task_color = task.get('{http://bpmn.io/schema/bpmn/biocolor/1.0}fill')
        if task_color in critical_path_colors(config.selected_colors):
            task_id = task.get('bpmnElement')
            color_dict[task_id] = task_color

def collect_edge_element_id_and_colors():
    #Collect Edge element ids and colors from color_dict dictionary
    global color_dict
    for task in root.iter('{http://www.omg.org/spec/BPMN/20100524/DI}BPMNEdge'):
        task_color = task.get('{http://bpmn.io/schema/bpmn/biocolor/1.0}fill')
        if task_color in critical_path_colors(config.selected_colors):
            task_id = task.get('bpmnElement')
            color_dict[task_id] = task_color

def delete_elements_not_on_critical_path():    
    #Select the the id and name of the process element if process element id is in the color dictionary 
    global process_element_ids    
    for task_id, name in process_element_ids.copy().items():
        if task_id not in color_dict.keys():
            del process_element_ids[task_id]

def extend_the_id_and_name_with_duration():
    #Extending the process element id and name with duration
    global process_element_ids
    for key, name in process_element_ids.items():
        if key in dict_durations.keys():
            process_element_ids[key].append(dict_durations[key])
        else:
            process_element_ids[key].append("No duration value")

def extend_list_with_key_type():
    #Adding key type to the list
    global process_element_ids
    for key, value in  process_element_ids.items():
        split = key.split('_')
        process_element_ids[key].append(split[0])

def create_csv_name():
    #Creating file name for csv creation
    global csv_file_name
    original_file_name = re.findall('([0-9a-zA-Z-_ ]+)\.', config.bpmn_file_name)
    csv_file_name = "{}-on-{}-at-{}.csv".format(
        original_file_name[0],
        datetime.date.today(),
        datetime.datetime.now().strftime('%H-%M-%S'))

def create_csv(csv_file_name):
    #Writing element id, name and duration to csv
    with open (csv_file_name, mode='w', newline='\n') as f:
        writer = csv.writer(f, delimiter = config.delimiter_char, quotechar = '"', quoting=csv.QUOTE_MINIMAL)
        for key in  process_element_ids.keys():
            writer.writerow(
                [process_element_ids[key][1].encode('unicode-escape').decode(),
                process_element_ids[key][2].encode('unicode-escape').decode(),
                key,
                process_element_ids[key][0].encode('unicode-escape').decode()]
                )
        print('CSV file created')

#Get the rgb value for colors on critical path
critical_path_colors = lambda selected_colors: [config.colors[color] for color in config.selected_colors]

tree = ET.parse(config.bpmn_file_name)
root = tree.getroot()

parent_map = {c.tag:p.tag for p in root.iter( ) for c in p}
parent_map_elements = {c:p for p in root.iter() for c in p}

elements_under_process = []
element_ids_under_process = []
dict_durations = {}
process_element_ids = {}
csv_file_name = ''

collect_elemets_under_process()
collect_elemet_ids_under_process()
collect_elemets_with_duration()
collect_element_id_and_name()

if config.critical_pass:

    color_dict = {}
    collect_shape_element_id_and_colors()
    collect_edge_element_id_and_colors()
    delete_elements_not_on_critical_path()
    
extend_the_id_and_name_with_duration()
extend_list_with_key_type()
create_csv_name()
create_csv(csv_file_name)
