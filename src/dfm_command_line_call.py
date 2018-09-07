import os
import sys
from subprocess import call

WORKING_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
ROOT = os.path.join(WORKING_DIR, '..')
TASKLIB = os.path.join(ROOT, 'src/')
INPUT_FILE_DIRECTORIES = os.path.join(ROOT, 'data/')

# command_line = "python "+TASKLIB+"download_from_manifest.py"\
#                 + " -m " + INPUT_FILE_DIRECTORIES+"gdc_minifest_20171221_005438.txt"\
#                 + " -n " + INPUT_FILE_DIRECTORIES+"metadata.cart.2017-12-21T21_41_22.870798.json"\
#                 + " -g True " + "-c True " + "-t False " + "-o demo"
#                 # + " -d"

# Debugging on 2018-05-17
command_line = "python "+TASKLIB+"download_from_manifest.py"\
                + " -m " + INPUT_FILE_DIRECTORIES+"LIHC_MANIFEST.txt"\
                + " -n " + INPUT_FILE_DIRECTORIES+"LIHC_METADATA.json"\
                + " -g True " + "-c True " + "-t True " + "-o demo"

# # # Debugging on 2018-09-06
# command_line = "python "+TASKLIB+"download_from_manifest.py"\
#                 + " -m " + INPUT_FILE_DIRECTORIES+"gdc_minifest_20171221_005438.txt"\
#                 + " -n " + INPUT_FILE_DIRECTORIES+"metadata.cart.2017-12-21T21_41_22.870798.json"\
#                 + " -g True " + "-c True " + "-t True " + "-o demo"

print("About to call the module using the command line:", command_line)

call(command_line, shell=True)
