from dfm_functions import *
import argparse

parser = argparse.ArgumentParser()
# ~~~~Arguments~~~~~ #
parser.add_argument("-m", "--manifest", type=str,
                    help="The relative path of the manifest used to download the data")
parser.add_argument("-n", "--metadata", type=str,
                    help="The relative path of the metadata file")
parser.add_argument("-o", "--output_file_name", type=str,
                    help="The basename to use for output files", default='TCGA_dataset')
parser.add_argument("-v", "--verbose", action="store_true",
                    help="increase output verbosity")
parser.add_argument("-d", "--debug", action="store_true",
                    help="increase output verbosity")
parser.add_argument("-g", "--gct", type=str,
                    help="create a corresponding gct file")
parser.add_argument("-c", "--cls", type=str,
                    help="create a corresponding cls file")
# parser.add_argument("-f", "--filename", type=str,
#                     help="filename of the gct file")
parser.add_argument("-t", "--translate", type=str,
                    help="translate ensembl id to hugo gene id")
args = parser.parse_args()
if args.verbose:
    print("We like being verbose!")

print("Using arguments:")
print(args)

# Download from manifest
# manifest = "gdc_manifest_20171221_005438.txt"
manifest = args.manifest
# metadata_file = "metadata.cart.2017-12-21T21_41_22.870798.json"
metadata_file = args.metadata

# pwd = os.path.dirname(__file__)
pwd = execute('pwd', doitlive=True)

command = "gdc-client download -m "+manifest  # This is for the docker container call

if args.debug:
    print("Debug mode on. Files assumed to be already present")
else:
    print("About to execute the command:", command)
    try:
        what = execute(command, doitlive=False)
    except NotADirectoryError:  # except FileNotFoundError:
        print("Global version of gdc-client not found, trying local version.")
        command = pwd + "/gdc-client download -m " + manifest  # This is for calling the gcd file locally
        print("About to execute the command:", command)
        what = execute(command)
    print('All files in manifest were downloaded, probably. To be sure, check the output of the gdc-client.')

dfest = pd.read_table(manifest)

# Parse metadata
meta_data = json.load(open(metadata_file))

# Make a dictionary to map file names to TCGA unique ID's
#   # if we wanted to have only one sample per patient per "phenotype" we could use this:
#   # meta_data[0]['cases'][0]['samples'][0]['submitter_id']
#   # But since we want a unique ID for each HTSeq file (some patient/phenotypes will have multiple vials/replicates):
#   # meta_data[0]['cases'][0]['samples'][0]['portions'][0]['analytes'][0]['aliquots'][0]['submitter_id']
#   # Read more hre: https://wiki.nci.nih.gov/display/TCGA/Understanding+TCGA+Biospecimen+IDs
name_id_dict = {}
for i in range(len(meta_data)):
    file_name = meta_data[i]['file_name']
    unique_id = meta_data[i]['cases'][0]['samples'][0]['portions'][0]['analytes'][0]['aliquots'][0]['submitter_id']
    name_id_dict[file_name] = unique_id

destination = os.path.join(pwd, 'raw_count_files')

if os.path.isdir(destination):
    shutil.rmtree(destination)
os.mkdir(destination)

file_list = []

for d, f in zip(dfest['id'], dfest['filename']):
    shutil.copy(os.path.join(d, f), destination)  # Move the downloaded files to a folder
    if not args.debug:
        shutil.rmtree(d)  # Remove those files/folders from current directory
    # "decompress" and remove gz files
    uncompress_gzip(os.path.join(destination, f), new_name=os.path.join(destination, name_id_dict[f]+'.htseq.counts'))
    file_list.append(os.path.join(destination, name_id_dict[f]+'.htseq.counts'))
print('All files were moved and "decompressed" successfully.')

print('Now creating the Sample Information file.')
make_sample_information_file(name=args.output_file_name+'_sampleinfo.txt', manifest_df=dfest, name_id_dict=name_id_dict)
print('Sample Information file created successfully!')

if (args.gct == 'True'):
    print('Now creating the GCT file.')
    make_gct(file_list, args.translate == 'True', args.output_file_name, args.cls == 'True')
    print('GCT file created successfully!')

    # This could be its own parameter, but for now only output raw files if GCT is not created
    # Now removing folders named: "unused_files" and "raw_count_files"
    print('Now removing some intermediate files.')
    for folder in ['raw_count_files', 'unused_files']:
        destination = os.path.join(pwd, folder)
        if os.path.isdir(destination):
            shutil.rmtree(destination)
    print('All intermediate files were removed. We are done!')
