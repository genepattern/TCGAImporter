import subprocess
from subprocess import call
import pandas as pd
import os
import shutil
import gzip
import json
import sys
import mygene


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


def execute(comando, doitlive=False, input_to_use=None, verbose=True):
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


def make_sample_information_file(name, manifest_df, name_id_dict):
    # name = 'TCGA_' + dataset_name + '.txt'
    file = open(name, 'w')
    file.write('File\tClass\tSample_Name\n')
    for f in manifest_df['filename']:

        # TODO: add a filter here for the types of samples we want. I am using all "0x"and "1x" samples...
        # but presumably we only want "01" and "11" but then we should remove those from the directory (moved them to "unused")

            if name_id_dict[f][13:15] == '01':
                # file.write('\t'.join([name_id_dict[f]+'.htseq',class_dict[name_id_dict[f][17:19]] ,name_id_dict[f]]))
                file.write('\t'.join([name_id_dict[f]+'.htseq', 'Tumor', name_id_dict[f]]))
                file.write('\n')
                # print(name_id_dict[f])
            elif name_id_dict[f][13:15] == '11':
                file.write('\t'.join([name_id_dict[f]+'.htseq', 'Normal', name_id_dict[f]]))
                file.write('\n')
                # print(name_id_dict[f])
            else:
                print('\tIgnoring file named "{}" because sample is neither Primary Tumor nor Matched Normal tissue '
                      '(i.e., sample id = {}).'.format(name_id_dict[f], name_id_dict[f][13:15]))
                # Move from raw_count_files to unused_files
                pwd = execute('pwd', doitlive=False, verbose=False)
                destination = os.path.join(pwd, 'unused_files')
                if os.path.isdir(destination):
                    shutil.rmtree(destination)
                os.mkdir(destination)
                # Move the downloaded files to a folder
                source = os.path.join(pwd, 'raw_count_files', name_id_dict[f]+'.htseq.counts')
                shutil.move(source, destination)
                # shutil.rmtree(os.path.join(pwd, 'raw_count_files'))  # Remove those files/folders from current directory
                # print(f)
                # print(name_id_dict[f]+'.htseq.counts')
    file.close()

    return


def make_gct(file_list, translate_bool, file_name, cls_bool):
    """
    This function makes a GCT file by concatenating all the files present in file_list
    """
    df_gct = None

    # get sample names
    sample_list = []
    # sample_list.append("GID")  # 2018-02-07 Changing this to Name
    sample_list.append("Name")
    # sample_list.append("NAME")  # 2018-02-07 Changing this to Description to conform to other GenePattern GCT files
    sample_list.append("Description")

    #CLS file generation
    #01 - 09 tumor, 10 - 19 normal, 20 - 29 control
    cls_list = []

    removed_for_repetition = 0

    # add data from every file in list to dataframe if exists
    for file in file_list:
        if os.path.exists(file):

            # get sample name
            splited = file.split('/')
            # # splited = splited[len(splited) - 1].split('.')[0][:19]  # After 15 IDs become redundant
            splited = splited[len(splited) - 1].split('.')[0][:15]

            if splited not in sample_list:

                sample_list.append(splited)
                cls_list.append(splited[-2:])

                # read in file
                df_curr = pd.read_table(file, header=None)

                # if first file, get gene translations and ensembl ids
                if df_gct is None:
                    df_gct = df_curr.copy()
                    df_curr.drop(df_curr.columns[1, ], axis=1, inplace=True)
                    df_curr[df_curr.columns[0]] = df_curr[df_curr.columns[0]].apply(lambda x: x.split(".")[0])

                    # print(df_curr[df_curr.columns[0]])
                    if translate_bool:
                        df_curr[df_curr.columns[0]] = df_curr[df_curr.columns[0]].apply(lambda x: translate(x))
                    df_gct = pd.concat([df_curr, df_gct], axis=1)

                # otherwise just concatenate
                else:
                    # get counts column and concatenate
                    df_curr.drop(df_curr.columns[0,], axis=1, inplace=True)
                    df_gct = pd.concat([df_gct, df_curr], axis=1)
            else:
                removed_for_repetition += 1

    print("{} samples were not included due to repetition, only one sample per unique ID is being used.".format(
        removed_for_repetition))

    # remove last 5 rows, which are not genes
    df_gct = df_gct[:-5]

    # start writing gct file
    f = open(str(file_name+".gct"), "w")
    # headers
    f.write("#1.2")
    #  # The next two lines add enough tabs, removed for now on 2018-02-07
    # for i in range(len(sample_list)):
    #     f.write('\t')
    f.write('\n')

    f.write(str(len(df_gct)) + "\t" + str((len(sample_list) - 2)))
    #  # The next two lines add enough tabs, removed for now on 2018-02-07
    # for i in range(len(sample_list) - 2):
    #     f.write('\t')
    f.write('\n')

    # sample names
    f.write('\t'.join(sample_list))
    # # The following lines do the same but add one extra tab
    # for i in range(len(sample_list)):
    #     f.write(sample_list[i])
    #     print(sample_list[i])
    #     f.write('\t')
    f.write('\n')

    # dataframe
    df_gct.to_csv(f, sep='\t', index=False, header=False)
    f.close()

    if cls_bool:
        print("cls_list= ", cls_list)
        # start writing cls file
        f = open(str(file_name+".cls"), "w")
        types = set(cls_list)
        # headers
        f.write(str(len(cls_list)))
        f.write(' ')
        f.write(str(len(types)))
        f.write(' 1\n#')

        type_dict = {}
        type_count = 0
        for t in types:
            type_dict[t] = type_count
            type_count += 1
            f.write(' ')
            f.write(t)
            print(t)

        f.write('\n')

        for val in cls_list[:-1]:
            f.write(str(type_dict[val]))
            f.write(' ')
        f.write(str(type_dict[cls_list[-1]]))

        f.close()

mg = mygene.MyGeneInfo()


def translate(ESNG):
    try:
        ID = mg.getgene(ESNG)['symbol']
    except TypeError:
        ID = ESNG
    return ID

class_dict = {
    '01': 'Tumor',
    '02': 'Tumor',
    '03': 'Tumor',
    '04': 'Tumor',
    '05': 'Tumor',
    '06': 'Tumor',
    '07': 'Tumor',
    '08': 'Tumor',
    '09': 'Tumor',
    '10': 'Normal',
    '11': 'Normal',
    '12': 'Normal',
    '13': 'Normal',
    '14': 'Normal',
    '15': 'Normal',
    '16': 'Normal',
    '17': 'Normal',
    '18': 'Normal',
    '19': 'Normal',
}
