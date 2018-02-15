import subprocess
from subprocess import call
import pandas as pd
import os
import shutil
import gzip
import json
import sys
import mygene

#filter based on columns, or samples, takes in gct file path and comma space delimited string
def filter_GCT_on_Samples(file_name, samples):
    samples = samples.split(', ')
    file = open(file_name)

    if not file.readline().startswith("#1.2"):
        print("incorrect file format")
    num_rows, num_samples = [int(x) for x in file.readline().split()]
    df_samples = pd.read_table(file)

    df_new = df_samples.iloc[:,0:2]
    sample_list = []
    sample_list.append("Name")
    sample_list.append("Description")

    for sample in samples:
        if sample in df_samples.columns:
            sample_list.append(sample)
            df_new = pd.concat([df_new, df_samples[sample].to_frame()], axis=1)
        else:
            print('Error cannot find ' + sample)
    file.close()

    # start writing gct file
    f = open(str(file_name+"_new.gct"), "w")
    # headers
    f.write("#1.2")
    f.write('\n')
    f.write(str(len(df_new)) + "\t" + str((len(sample_list) - 2)))
    f.write('\n')
    # sample names
    f.write('\t'.join(sample_list))
    f.write('\n')
    # dataframe
    df_new.to_csv(f, sep='\t', index=False, header=False)
    f.close()

#filter based on rows, or genes, takes in gct file path and comma space delimited string
def filter_GCT_on_Genes(file_name, genes):
    genes = genes.split(', ')
    file = open(file_name)

    if not file.readline().startswith("#1.2"):
        print("incorrect file format")
    num_rows, num_samples = [int(x) for x in file.readline().split()]
    df_samples = pd.read_table(file)

    gene_names = df_samples['Name'].unique()
    for gene in genes:
        if gene not in gene_names:
            print('Error cannot find ' + gene)
    sample_list = df_samples.columns
    df_new = df_samples.loc[df_samples['Name'].isin(genes)]
    file.close()

    # start writing gct file
    f = open(str(file_name+"_new.gct"), "w")
    # headers
    f.write("#1.2")
    f.write('\n')
    f.write(str(len(df_new)) + "\t" + str((len(sample_list) - 2)))
    f.write('\n')
    # sample names
    f.write('\t'.join(sample_list))
    f.write('\n')
    # dataframe
    df_new.to_csv(f, sep='\t', index=False, header=False)
    f.close()

#samples = 'TCGA-EW-A3E8-01, TCGA-BH-A0B9-01'
#filter_GCT_on_Samples('./demo.gct', samples)
#genes = 'ENSG00000000003, ENSG00000001617'
#filter_GCT_on_Genes('./demo.gct', genes)