# utility file with srcML helper functions
import os
import shutil



# convert project directory to srcML directory
def dir_to_xml(path):
    working_directory = path + '_sliced'
    shutil.copytree(path, working_directory)
    for (root,dirs,files) in os.walk(working_directory, topdown=True):
        for source_file in files:
            file_extension = determine_extension(source_file)
            if (file_extension == 'invalid' or file_extension == 'xml'):
                continue
            else:
                file_path = root + '/' + source_file
                xml_source = file_path.strip(file_extension) + 'xml'
                os.system('./srcml ' + file_path + ' -o ' + xml_source)
                os.system('rm ' + file_path)
    

# converts the srcML code in the cloned directory back to slice code
def xml_to_dir(path): #call this function with the original path, not the '[original]_sliced' path
    working_directory = path + '_sliced'
    for (root,dirs,files) in os.walk(working_directory, topdown=True):
        for source_file in files:
            if (determine_extension(source_file) == 'xml'):
                file_path = root + '/' + source_file
                print(file_path)
                os.system('./srcml --to-dir . ' + file_path)
                os.system('rm ' + file_path)

def determine_extension(src):
    valid_extensions = ['xml','c', 'cpp', 'cc', 'java', 'cs'] #extensions supported by srcML
    extension = src.split('.')[-1]
    if valid_extensions.count(extension) == 1:
        return extension
    else:
        return 'invalid'