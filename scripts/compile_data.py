from git import Repo
from xml.etree import ElementTree
import pathlib
from pprint import pprint


XML_FOLDER_PATH = "../data/dataset"


def retrieve_xml_file_paths(folder_path: str) -> [pathlib.Path]:
    """
    Retrieve all the xml files in the given folder_path
    :param folder_path: the path to the folder containing the xml files
    :return: A list of the xml file paths in the given folder_path
    """
    path = pathlib.Path(folder_path)
    return [i for i in path.glob("*.xml")]


def retrieve_file_at_commit(repo_path: str, commit_sha: str) -> dict:
    ...


if __name__ == "__main__":
    pprint(retrieve_xml_file_paths(XML_FOLDER_PATH))

