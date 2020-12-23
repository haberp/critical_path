from lxml import etree as ET

tree = ET.parse(r'C:\Users\vajda\Documents\Python programok\EDM - Consumption data collection at UK & Continental Europe.bpmn')
root = tree.getroot()

elements = {}

for element in root.iter():
    if element.get('id') != None:
        element_id = element.get('id')
    elements[element] = {'id': element_id}
    for key, value in element.attrib.items():
        new_values = {key: value}
        #print(new_values)
        elements[element].update(new_values)

for key, value in elements.items():
    print(key, value)