import subprocess
from subprocess import call
import pandas as pd
import os
import shutil
import gzip
import json
import sys


def uncompress_gzip(file_name, new_name=None, delete=True):
    # Read the stream and write that stream to a new file:
    in_file = gzip.open(file_name, 'rb')
    if new_name is None:
        out_file = open(file_name.strip('.gz'), 'wb')
    else:
        out_file = open(new_name, 'wb')
    out_file.write(in_file.read())
    in_file.close()
    out_file.close()
    if delete:
        os.remove(file_name)


def execute(comando, doitlive=False, input_to_use=None):
    # result = subprocess.run(['ls', '-l'], stdout=subprocess.PIPE)
    comando = comando.split(' ')

    if doitlive:
        popen = subprocess.Popen(comando, stdout=subprocess.PIPE, universal_newlines=True)
        to_return = popen.stdout.read()
        for line in to_return:
            print(line, end='')
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, comando)
    else:
        if input_to_use is not None:
            input_to_use = input_to_use.ecode('utf-8')
        result = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=input_to_use)
        to_return = result.stdout.decode('utf-8')
        print(to_return)
    return to_return.strip('\n')


def make_sample_information_file():

    return
