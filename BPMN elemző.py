#This program processes an xml file created by a process modelling tool and exports process elements and their selected data into a csv file
#Creator: Peter Haber
#Version: 2.0

import xmltodict
import config
import csv
import re
import datetime
import pprint
import xml.etree.ElementTree as ET
import collections

def create_csv_name():
    #Create formatted file name
    original_file_name = re.findall('([0-9a-zA-Z-_ ]+)\.', r'C:\Users\vajda\Documents\Python programok\EDM - Consumption data collection at UK & Continental Europe.bpmn')
    csv_file_name = "{}-on-{}-at-{}.csv".format(
        original_file_name[0],
        datetime.date.today(),
        datetime.datetime.now().strftime('%H-%M-%S'))
    return csv_file_name

def create_csv(csv_file_name):
    #Write collected data to csv
    with open (csv_file_name, mode='w', newline='\n') as f:
        writer = csv.writer(f, delimiter = config.delimiter_char, quotechar = '"', quoting=csv.QUOTE_MINIMAL)
        for element in result:
            writer.writerow(
                [element[3],
                element[1],
                element[0],
                element[2],
                ])
        print('CSV file created')

def add_name(dictionary):
    result[-1].append(dictionary['@name'])

def add_no_description():
    result[-1].append('No description')

def add_no_duration():
    result[-1].append('No duration')

tree = ET.parse(r'C:\Users\vajda\Documents\Python programok\EDM - Consumption data collection at UK & Continental Europe.bpmn')
xml_data = tree.getroot()
xmlstr = ET.tostring(xml_data, encoding='utf-8', method='xml')
elements = dict(xmltodict.parse(xmlstr))
result = [("Id", "Type", "Description", "Duration")]
process_elements = [key for key in elements['ns0:definitions']['ns0:process'].keys() if key.startswith('ns0')]

for element in process_elements:
    element_path = elements['ns0:definitions']['ns0:process'][element]
    for dictionary in element_path:
        if type(dictionary) is collections.OrderedDict:
            result.append(
                [dictionary['@id'],
                dictionary['@id'].split('_')[0]
                ])
            try:
                add_name(dictionary)
            except KeyError:
                add_no_description(dictionary)
            try:
                result[-1].append(dictionary['ns0:extensionElements']['ns1:properties']['ns1:property'].get('@value'))
            except KeyError:
                add_no_duration()
        else:
            result.append(
                [element_path['@id'],
                element_path['@id'].split('_')[0]
                ])
            try:
                result[-1].append(element_path['@name'])
            except KeyError:
                add_no_description(dictionary)
            try:
                result[-1].append(element_path['ns0:extensionElements']['ns1:properties']['ns1:property'].get('@value'))
            except KeyError:
                add_no_duration()
            break

create_csv_name()
create_csv(create_csv_name())
