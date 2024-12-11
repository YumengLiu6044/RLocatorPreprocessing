from git import Repo
from xml.etree import ElementTree
from pathlib import Path
from pprint import pprint
import os


XML_FOLDER_PATH = "../data/dataset/"


def retrieve_xml_file_paths(folder_path: str) -> [Path]:
    """
    Retrieve all the xml files in the given folder_path
    :param folder_path: the path to the folder containing the xml files
    :return: A list of the xml file paths in the given folder_path
    """
    path = Path(folder_path)
    return [i for i in path.glob("*.xml")]


def retrieve_bug_reports(xml_file_path: Path) -> [dict]:
    """
    Retrieve the bug reports from the given xml file
    :param xml_file_path: Path object to the xml file
    :return: a list of the bug reports as a dictionary
    """
    xml_tree = ElementTree.parse(xml_file_path)
    bug_reports = []
    for table in xml_tree.findall("./database/"):
        table_dict = {
            entry.attrib["name"]: entry.text for entry in table
        }
        bug_reports.append(table_dict)

    return bug_reports


def retrieve_file_at_commit(repo_path: Path, commit_sha: str) -> dict:
    ...


if __name__ == "__main__":
    sample_file_path = os.path.join(XML_FOLDER_PATH, "AspectJ.xml")
    sample_file_path = Path(sample_file_path)
    retrieve_bug_reports(sample_file_path)

