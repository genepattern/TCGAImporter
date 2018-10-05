# 2018-10-05
# Building a zip file for GenePattern -- ASSUMING THIS IS FOR A PRE-RELEASE

import subprocess

def run(comando, doitlive=True, input_to_use=None, verbose=True):
    # result = subprocess.run(['ls', '-l'], stdout=subprocess.PIPE)
    comando = comando.split(' ')

    if doitlive:
        popen = subprocess.Popen(comando, stdout=subprocess.PIPE, universal_newlines=True)

        to_return = popen.stdout.read()
        for line in to_return:
            if verbose:  # I see no reason to doitlive and have it be not verbose, but to each their own.
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
        if verbose:
            print(to_return)
    return to_return.strip('\n')

# Get the name of the module:
with open('manifest', 'r') as f:
    for line in f.readlines():
        if 'name=' in line:
            module_name = line.strip('\n')
            module_name = module_name.replace('name=','')
            module_name = module_name.replace(' ','')  #Just in case there were any spaces
            break  #These are indeed the droids we are looking for! Move along!
    print("Accodring to the manifest the module's name is:", module_name)

# Get figure out the version:
with open('release.version', 'r') as f:
    line = f.readlines()[-1].strip('\n')
    major = int(line[-1]) - 1  # If this is a full release, we should not do the -1
    print("Current major version is:", major)

with open('prerelease.version', 'r') as f:
    line = f.readlines()[-1].strip('\n')
    minor = int(line[-1])  # If this is a full release, this should be set to 0
    print("Current minor version is:", minor)

version = str(major)+'.'+str(minor)
print("Hence, the version of this zip file will be:", version)

# Create a zip file
files_to_zip = ["manifest",
                "doc.html",
                "src/dfm_command_line_call.py",
                "src/dfm_functions.py",
                "src/download_from_manifest.py",
                "src/filter_gct.py",
                "src/TCGA_ENSEMBL2HUGO_dictionary.p"]
print("Addding these files to the zip:",files_to_zip)
print("about to run this command",f'zip -j {module_name+".v"+version+".zip"} {" ".join(files_to_zip)}')
run(f'zip -j {module_name+".v"+version+".zip"} {" ".join(files_to_zip)}')
