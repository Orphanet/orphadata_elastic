import copy
import re

import json
import pathlib
import time

import orphadata_elastic
import config_orphadata_elastic as config

"""
Alternative process to treat Orphadata classification
"""


class Node(dict):
    def __init__(self):
        super().__init__()
        self["name"] = ""
        self["ORPHAcode"] = ""
        self["hch_id"] = ""
        self["hch_tag"] = ""
        self["parents"] = []
        self["childs"] = []


def parse_plator(pat_hch_path):
    """
    Parse PatHch.Txt (plator extract) to create a dictionary to convert hch_id to hch_tag
    DEPRECATED: classification xml now output the hch label

    :param pat_hch_path:
    :return: hch_dict: dictionary to convert hch_id to hch_tag
    """
    hch_dict = {}
    with open(pat_hch_path, "r") as ini:
        header = ini.readline()[:-1].split("\t")
        hch_id_index = header.index("HchId")
        hch_tag_index = header.index("HchTag (english label)")
        lng_index = header.index("Lng")
        for line in ini:
            data = line[:-1].split("\t")
            if data[lng_index] == "en":
                hch_dict[data[hch_id_index]] = data[hch_tag_index]
    # print(hch_dict)
    return hch_dict


def make_node_dict(node_dict, xml_dict, hch_id, hch_tag, parent):
    """
    Recursively parse xml_dict to output a collection of Disorder with all their children

    :param node_dict: Dictionary of Disorders i.e.
    {2846: {
        "name": "Congenital pericardium anomaly",
        "OrphaNumber": "2846",
        "hch_id": "148",
        "parents": ["97965"],
        "childs": ["99129", "99130", "99131"]
        },
    2847: {...}
    }
    :param hch_id: String, Orphanet classification number
    :param hch_tag: String, Orphanet classification tag
    :param xml_dict: xml source file parsed as a dictionary
    :param parent: Orpha_ID of parent Disorder
    :return: node_dict
    """
    # print(xml_dict)
    node = Node()
    node["ORPHAcode"] = xml_dict["Disorder"]["ORPHAcode"]
    node["name"] = xml_dict["Disorder"]["Name"]
    node["hch_id"] = hch_id
    node["hch_tag"] = hch_tag
    node["parents"] = [parent]
    # print(node)
    if xml_dict["ClassificationNodeChild"] is not None:
        for child in xml_dict["ClassificationNodeChild"]:
            node["childs"].append(child["Disorder"]["ORPHAcode"])
            node_dict = make_node_dict(node_dict, child, hch_id, hch_tag, node["ORPHAcode"])
    if node["ORPHAcode"] in node_dict:
        node_dict[node["ORPHAcode"]]["childs"] = merge_unique(node_dict[node["ORPHAcode"]]["childs"], node["childs"])
        node_dict[node["ORPHAcode"]]["parents"] = merge_unique(node_dict[node["ORPHAcode"]]["parents"], node["parents"])
        # print(node_dict[node.OrphaNumber].childs)
    else:
        node_dict[node["ORPHAcode"]] = node
    return node_dict


def merge_unique(list1, list2):
    """
    Merge two list and keep unique values
    """
    for item in list2:
        if item not in list1:
            list1.append(item)
    return list1


def convert(hch_id, xml_dict):
    """
    :param hch_id: String, Orphanet classification number
    :param xml_dict: xml source file parsed as a dictionary
    :return: node_list: List collection of Disorder
    i.e.:
    [
    {"name": "Congenital pericardium anomaly",
    "OrphaNumber": "2846",
    "hch_id": "148",
    "parents": ["97965"],
    "childs": ["99129", "99130", "99131"]
    },
    {...}
    ]
    """
    start = time.time()

    hch_tag = xml_dict["Name"]

    xml_dict = xml_dict["ClassificationNodeRoot"][0]

    parent = xml_dict["Disorder"]["ORPHAcode"]

    node_dict = {}
    node_dict = make_node_dict(node_dict, xml_dict, hch_id, hch_tag, parent)

    node_list = list(node_dict.values())

    # print(node_list)
    print(len(node_list), "disorder concepts")

    print(time.time() - start, "s")
    return node_list


def process_classification(in_file_path, out_folder, elastic, input_encoding, indent_output, output_encoding):
    """
    Complete Orphadata XML to Elasticsearch JSON process

    :param in_file_path: input file path
    :param out_folder: output folder path
    :param elastic: URI to elastic node, False otherwise
    :param input_encoding:
    :param indent_output: indent output file (True for visual data control, MUST be False for elasticsearch upload)
    :param output_encoding:
    :return: None (Write file (mandatory) / upload to elastic cluster)
    """

    file_stem = in_file_path.stem.lower()
    if "CZ" in file_stem:
        file_stem = file_stem.replace("CZ", "CS")
    if "cz" in file_stem:
        file_stem = file_stem.replace("cz", "cs")

    # Remove the suffixed date
    file_stem = re.sub("_[0-9]{4}(?![0-9])", "", file_stem)

    index = config.index_prefix
    if index:
        index = "{}_{}".format(index, file_stem)
    else:
        index = file_stem
    print(file_stem)
    out_file_name = index + ".json"
    out_file_path = out_folder / out_file_name

    hch_id = file_stem.split("_")[2]

    # Parse source xml file and return the date also reroot the xml to skip the trivial JDBOR/*List/
    xml_dict, extract_date = orphadata_elastic.parse_file(in_file_path, input_encoding, False)
    xml_dict = orphadata_elastic.subset_xml_dict(xml_dict)

    start = time.time()
    # remove intermediary dictionary (xml conversion artifact) and rename OrphaNumber
    rename_orpha = True  # OrphaNumber to ORPHAcode
    xml_dict = orphadata_elastic.simplify(xml_dict, rename_orpha)

    node_list = convert(hch_id, xml_dict)

    if config.cast_as_integer:
        node_list = orphadata_elastic.remap_integer(node_list)

    print("convert:", time.time() - start, "s")

    # Output/upload function
    orphadata_elastic.output_process(out_file_path, index, node_list, elastic, indent_output, output_encoding)
