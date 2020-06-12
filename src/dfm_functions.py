import subprocess
from subprocess import call
import pandas as pd
import os
import shutil
import gzip
import json
import sys
import mygene
import pickle


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

    # pwd = execute('pwd', doitlive=False, verbose=False)
    # destination = os.path.join(pwd, 'unused_files')
    # if os.path.isdir(destination):
    #     shutil.rmtree(destination)

    # name = 'TCGA_' + dataset_name + '.txt'
    file = open(name, 'w')
    file.write('File\tClass\tSample_Name\n')
    ignored_files = []
    ignored_twice = []
    ignored_flag = False
    for f in manifest_df['filename']:

        # TODO: add a filter here for the types of samples we want. I am using all "0x"and "1x" samples...
        # but presumably we only want "01" and "11" but then we should remove those from the directory (moved them to "unused")

            if name_id_dict[f][13:15] == '01':
                # file.write('\t'.join([name_id_dict[f]+'.htseq',class_dict[name_id_dict[f][17:19]] ,name_id_dict[f]]))
                file.write('\t'.join([name_id_dict[f]+'.htseq', 'Tumor', name_id_dict[f]]))
                file.write('\n')
                # print(name_id_dict[f])
            elif name_id_dict[f][13:15] == '03':
                print('\tNot ignoring file named "{}" because sample is tagged as'
                      ' "Primary Blood Derived Cancer - Peripheral Blood"'
                      '(i.e., sample id = {}), this is usually expected for LAML.'
                      .format(name_id_dict[f], name_id_dict[f][13:15]))
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
                if name_id_dict[f] not in ignored_files:
                    ignored_flag = True
                    ignored_files.append(name_id_dict[f])  #keeping a list of the files which have been deleted prevent double deletion.
                    pwd = execute('pwd', doitlive=False, verbose=False)
                    destination = os.path.join(pwd, 'unused_files')
                    # if os.path.isdir(destination):
                    #     shutil.rmtree(destination)
                    if not os.path.isdir(destination):
                        os.mkdir(destination)
                    # Move the downloaded files to a folder
                    source = os.path.join(pwd, 'raw_count_files', name_id_dict[f]+'.htseq.counts')
                    print("source", source)
                    print("destination", destination)
                    # try:
                    shutil.move(source, os.path.join(destination, name_id_dict[f]+'.htseq.counts'))
                    # except shutil.Error:
                    #     shutil.move(source, destination)

                    # shutil.rmtree(os.path.join(pwd, 'raw_count_files'))  # Remove those files/folders from current directory
                    # print(f)
                    # print(name_id_dict[f]+'.htseq.counts')
                else:
                    print("This sample has been removed already only one sample with the same ID is allowed. "
                          "Consider setting 'long IDs' to 'True'"
                          "[as of 2018-07-06 this feature is yet to be implemented]")
                    ignored_twice.append(name_id_dict[f])
    file.close()

    if ignored_flag:
        print("The following files were ignored due to having the same ID as other sample:")
        print(ignored_twice)
    return


def remove_duplicate_genes(df):
    """
    TCGA has two duplicated genes RGS5 and POLR2J4.
    Rather than getting them manually, we'll check for all duplicated genes.
    """

    try:
        new_ix = df.index.droplevel(1).values
        df.index = new_ix
    except AttributeError:
        print("Dataframe only has one index, that's alright.")
    except IndexError:
        print("Using Pandas>1.0; Dataframe only has one index, that's alright.")
    except ValueError:
        print("Dataframe only has one index but it thinks it's multi-indexed, that's weird but alright.")

    # print(df)
    # print("")
    # print(df.columns)
    # print('getting first row')
    # print(df.ix[1,:])
    # print('getting first column')
    # print(df.ix[:, 0].ix[:, 0])
    # print('index')
    # print(df.index)
    # print(df.index.values)

    s = pd.Series(df['Name'])
    # print(s)
    import numpy as np
    repeated = s[s.duplicated()]
    repeated = np.unique(repeated.values)

    # print("---")
    # print(s)
    # print("@@@@@@@@@@")
    # print("Repeated are")
    # print(repeated)
    print(f"There were {len(repeated)} repeated genes.")
    print("Note that mygene.info's ENSEMBL ID to HUGO ID are not a 1 to 1 mapping, hence the replication.")
    df.set_index('Name', inplace=True)
    # print(df.head())
    # print(df.loc['TSPAN6',:])
    print(repeated)

    for gene in repeated:
        # if gene == 'RF00019':
        #     # print(gene)
        #     temp = df.loc[gene, :]
        #     df.drop(gene, axis=0, inplace=True)
        #     # print('before:')
        #     # print(temp)
        #     # print('after max:')
        #     temp_max = temp.max(axis=0, numeric_only=True)
        #     # print(temp_max)
        #     # temp_max.insert(0, 'ENSEMBL ID', 'Multiple ENSEMBL IDs')
        #     temp_max = pd.concat([pd.Series(['Multiple ENSEMBL IDs']), temp_max])
        #     # print(temp_max)
        #     columns = temp_max.values
        #     # columns = columns[-1:] + columns[:-1]  # Moving the ENSEMBL IDs first
        #     # print(columns)
        #
        #     df.loc[gene] = columns
        #     # print('after collapse')
        #     # print(df.loc[gene])
        #     # exit(192)

        # temp = df.loc[gene,:]
        # df.drop(gene, axis=0, inplace=True)
        # df.loc[gene] = temp.max(axis=0)
        # if gene == 'RF00019':
        temp = df.loc[gene,:]
        df.drop(gene, axis=0, inplace=True)
        temp_max = temp.max(axis=0, numeric_only=True)
        temp_max = pd.concat([pd.Series(['Multiple ENSEMBL IDs']), temp_max])
        df.loc[gene] = temp_max.values

    return df


def make_gct(file_list, translate_bool, file_name, cls_bool):
    """
    This function makes a GCT file by concatenating all the files present in file_list
    """
    df_gct = None

    if translate_bool:
        print('translation done with mygene.info')

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
                df_curr.columns = ['ENSEMBL ID', 'Counts']

                # if first file, get gene translations and ensembl ids
                if df_gct is None:
                    df_gct = df_curr.copy()
                    df_curr.drop(df_curr.columns[1, ], axis=1, inplace=True)
                    df_curr[df_curr.columns[0]] = df_curr[df_curr.columns[0]].apply(lambda x: x.split(".")[0])

                    if translate_bool:
                        print("Translating genes now")
                        df_curr[df_curr.columns[0]] = df_curr[df_curr.columns[0]].apply(lambda x: translate(x))
                    df_curr.columns = ['Name']
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

    # remove repeated genes
    df_gct = remove_duplicate_genes(df_gct)

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
    df_gct.to_csv(f, sep='\t', index=True, header=False)
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
try:
    with open('TCGA_ENSEMBL2HUGO_dictionary.p', 'rb') as handle:
        ENSEMBL2HUGO = pickle.load(handle)
except FileNotFoundError:
    try:
        print("Local version of dictionary not found, trying to explicitly add the PWD")
        pwd = os.path.dirname(os.path.realpath(__file__))
        print(pwd)
        with open(pwd+'/TCGA_ENSEMBL2HUGO_dictionary.p', 'rb') as handle:
            ENSEMBL2HUGO = pickle.load(handle)
    except FileNotFoundError:
        print("Local version of dictionary not found again, trying the docker container version")
        with open('/usr/local/bin/TCGAImporter/TCGA_ENSEMBL2HUGO_dictionary.p', 'rb') as handle:
            ENSEMBL2HUGO = pickle.load(handle)


def translate(ESNG):
    hugo_id = ESNG
    try:
        hugo_id = ENSEMBL2HUGO[ESNG]
    except KeyError:
        try:
            hugo_id = mg.getgene(ESNG)['symbol']
        except TypeError:
            hugo_id = ESNG
    return hugo_id

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
