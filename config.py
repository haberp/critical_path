critical_pass = True #Set critical_pass True or False
delimiter_char = ";" #Provide a csv separator
selected_colors = ["orange", "blue"] #enter the colors of critical path - "orange", "blue"
bpmn_file_name = 'C:/Users/peter/Downloads/EDM - Consumption data quality check - exp.bpmn' # Provide the path of the bpmn file
process_elements = [
    '{http://www.omg.org/spec/BPMN/20100524/MODEL}subProcess',
    '{http://www.omg.org/spec/BPMN/20100524/MODEL}process',
    '{http://www.omg.org/spec/BPMN/20100524/MODEL}laneSet'
    ]
colors = {
    "orange" : 'rgb(251, 140, 0)',
    "blue" : 'rgb(187, 222, 251)',
    "green" : 'rgb(67, 160, 71)',
    "red" : 'rgb(229, 57, 53)',
    "purple" : 'rgb(142, 36, 170)',
    }