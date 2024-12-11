from git import Repo
from xml.etree import ElementTree
from pathlib import Path
from pprint import pprint
import os


XML_FOLDER_PATH = "../data/dataset/"
xml_files_and_git_repo = {
    'Birt.xml': "https://git.eclipse.org/r/p/birt/org.eclipse.birt",
    'Eclipse_Platform_UI.xml': "https://git.eclipse.org/r/p/platform/eclipse.platform.ui",
    'AspectJ.xml': "git://git.eclipse.org/gitroot/aspectj/org.aspectj.git",
    'JDT.xml': "https://git.eclipse.org/r/p/jdt/eclipse.jdt.ui",
    'SWT.xml': "https://git.eclipse.org/r/p/platform/eclipse.platform.swt",
    'Tomcat.xml': "git://git.apache.org/tomcat.git"
}


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


def retrieve_file_at_commit(repo_url: Path, commit_sha: str) -> dict:
    ...


if __name__ == "__main__":
    sample_file_path = os.path.join(XML_FOLDER_PATH, "AspectJ.xml")
    sample_file_path = Path(sample_file_path)
    reports: [dict] = retrieve_bug_reports(sample_file_path)
    resolved_categories = set(report["status"] for report in reports)

    def count_frequency(category: str) -> int:
        return sum(report["status"] == category for report in reports)

    resolved_frequencies = {cat: count_frequency(cat) for cat in resolved_categories}
    pprint(resolved_frequencies)
