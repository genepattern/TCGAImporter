import os
import sys
from subprocess import call

WORKING_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
ROOT = os.path.join(WORKING_DIR, '..')
TASKLIB = os.path.join(ROOT, 'src/')
INPUT_FILE_DIRECTORIES = os.path.join(ROOT, 'data/')

command_line = "python "+TASKLIB+"download_from_manifest.py"\
                + " -m " + INPUT_FILE_DIRECTORIES+"gdc_manifest_20171221_005438.txt"\
                + " -n " + INPUT_FILE_DIRECTORIES+"metadata.cart.2017-12-21T21_41_22.870798.json"\
                + " -g True " + "-c True " + "-t False " + "-o demo"
                # + " -d"

print("About to call the module using the command line:", command_line)

call(command_line, shell=True)
