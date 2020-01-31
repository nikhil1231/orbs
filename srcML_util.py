# utility file with srcML helper functions
import os
import shutil
import xml.etree.ElementTree as ET

# clone project directory and convert target file
def clone_and_convert_target(directory_path, target_file_path):
    working_directory = directory_path + '_sliced'
    if (os.path.isdir(working_directory)):
        shutil.rmtree(working_directory)
    shutil.copytree(directory_path, working_directory)
    target_file_path = os.path.join(working_directory, target_file_path)
    file_extension = determine_extension(target_file_path)
    if (file_extension != 'invalid' and file_extension != 'xml'):
        xml_source = target_file_path.strip(target_file_path) + 'xml'
        os.system('./srcml ' + target_file_path + ' -o ' + xml_source)
        os.system('rm ' + target_file_path)
    return working_directory

# converts the srcML code in the cloned directory back to slice code
def convert_to_source(directory_path, target_file_path): #call this function with the original path, not the '[original]_sliced' path
    working_directory = directory_path + '_sliced'
    target_file_path = os.path.join(working_directory, target_file_path)
    if (check_xml(target_file_path)):
        os.system('./srcml --to-dir . ' + target_file_path)
        os.system('rm ' + target_file_path)
    

def determine_extension(src):
    valid_extensions = ['xml','c', 'cpp', 'cc', 'java', 'cs'] #extensions supported by srcML
    extension = src.split('.')[-1]
    if valid_extensions.count(extension) == 1:
        return extension
    else:
        return 'invalid'

def check_xml(src):
    extension = src.split('.')[-1]
    if extension == 'xml':
        tree = ET.parse(src)
        root = tree.getroot()
        if root.tag == '{http://www.srcML.org/srcML/src}unit':
            return 1
        else:
            return 0
    else:
        return 0
