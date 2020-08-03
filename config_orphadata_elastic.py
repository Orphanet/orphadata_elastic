import pathlib


# Single file input
import elasticsearch

in_file_path = pathlib.Path("C:\\Users\\Cyrlynx\\PycharmProjects\\data_RDcode\\Orphanet_Nomenclature_Pack_EN\\en\\ORPHAclassification_146_Rare_cardiac_disease_en.xml")

# List of path to folder containing data
folders = list()

####### API Orphadata ########
# Product 1 cross-reference
folders.append(pathlib.Path("data_in\\data_xml\\Disorders cross referenced with other nomenclatures"))

# Product 3 Classifications
pat_hch_path = pathlib.Path("data_in\\PatHch.Txt")
folders.append(pathlib.Path("data_in\\data_xml\\Orphanet classifications"))

# Product 4 HPO, phenotype
folders.append(pathlib.Path("data_in\\data_xml\\Phenotypes associated with rare disorders"))

# Product 6 Disorder => Gene, (output also Gene => Disorder)
folders.append(pathlib.Path("data_in\\data_xml\\Disorders with their associated genes"))

# Product 9
folders.append(pathlib.Path("data_in\\data_xml\\Epidemiological data\\Rare disease epidemiology"))
folders.append(pathlib.Path("data_in\\data_xml\\Epidemiological data\\Natural history"))
##############################

####### RDcode ########
# RDcode /!\ remember to change index_prefix
# folders.append(pathlib.Path("..\\data_RDcode_2020\\Orphanet_Nomenclature_Pack_EN"))
# folders.append(pathlib.Path("..\\data_RDcode_2020\\Orphanet_Nomenclature_Pack_EN\\en"))
# folders.append(pathlib.Path("..\\data_RDcode_2020\\Orphanet_Nomenclature_Pack_PL"))

# for lang in ["CS", "DE", "EN", "ES", "FR", "IT", "NL", "PL", "PT"]:
#     folders.append(pathlib.Path("..\\data_RDcode_2020\\Orphanet_Nomenclature_Pack_{}".format(lang)))
#     folders.append(pathlib.Path("..\\data_RDcode_2020\\Orphanet_Nomenclature_Pack_{}\\{}".format(lang, lang.lower())))
#########################

out_folder = pathlib.Path("data_out")

# Process all input folders or single input file ?
parse_folder = True

# input encoding: "auto" or valid encoding ("UTF-8" or "iso-8859-1")
input_encoding = "auto"

# ###################################################### OUTPUT ########################################################

# The prefix MUST be 'rdcode' for RDcode API (lowercase index name is mandatory)
# Empty string or False otherwise
index_prefix = ""

# Remap number as integer
cast_as_integer = True

# Indent output file (True for visual data control, need to be False for elasticsearch upload)
indent_output = False

# Upload to elasticsearch node
upload = True
elastic_node = elasticsearch.Elasticsearch(hosts=["localhost"])

# Make the yaml schema description
make_schema = False

output_encoding = "UTF-8"
