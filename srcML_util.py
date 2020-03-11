# utility file with srcML helper functions
import os
import shutil
import xml.etree.ElementTree as ET

srcml_exec_path = './srcml'

# clone project directory and convert target file


def clone_and_convert_target(directory_path, target_file_path):
    import random
    import sys

    # giving sliced dir a temporary name
    working_directory = directory_path + f'_{random.randint(0, sys.maxsize)}' + '_sliced'
    assert(not os.path.isdir(working_directory))
    shutil.copytree(directory_path, working_directory)

    full_target_file_path = os.path.join(working_directory, target_file_path)
    file_extension = determine_extension(full_target_file_path)
    assert(file_extension != 'invalid' and file_extension != 'xml')

    xml_source = full_target_file_path[:-len(file_extension)] + 'xml'
    os.system(f'{srcml_exec_path} {full_target_file_path} -o {xml_source}')
    return working_directory

# converts the srcML code in the cloned directory back to slice code


def convert_to_source(working_directory, xml_file_path):  # call this function with the '[original]_sliced' path
    full_xml_path = os.path.join(working_directory, xml_file_path)
    assert(check_xml(full_xml_path))
    tree = ET.parse(full_xml_path).getroot()
    os.system(f'{srcml_exec_path} {full_xml_path} -o {tree.attrib["filename"] }')


def determine_extension(src):
    valid_extensions = ['xml', 'c', 'cpp', 'cc', 'java', 'cs']  # extensions supported by srcML
    extension = src.split('.')[-1]
    if extension in valid_extensions:
        return extension
    else:
        return 'invalid'


def check_xml(src):
    extension = determine_extension(src)
    if extension == 'xml':
        tree = ET.parse(src)
        root = tree.getroot()
        if root.tag == '{http://www.srcML.org/srcML/src}unit':
            return True
    return False
