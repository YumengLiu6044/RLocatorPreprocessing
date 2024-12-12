from git import Repo
import pandas as pd
from pathlib import Path
from pprint import pprint
import os
import shutil
from xml.etree import ElementTree
import re
import tqdm
import zipfile

DATA_FOLDER_PATH = "/kaggle/input/bug-report-data/dataset"
project_repo_mapping = {
    'Birt.xml': "https://github.com/eclipse-birt/birt.git",
    'Eclipse_Platform_UI.xml': "https://github.com/eclipse-platform/eclipse.platform.ui.git",
    'AspectJ.xml': "https://github.com/eclipse-aspectj/aspectj.git",
    'JDT.xml': "https://github.com/eclipse-jdt/eclipse.jdt.ui.git",
    'SWT.xml': "https://github.com/eclipse-platform/eclipse.platform.swt.git",
    'Tomcat.xml': "https://github.com/apache/tomcat.git"
}


def retrieve_bug_reports(xml_file_path: Path) -> pd.DataFrame | None:
    """
    Retrieve the bug reports from the given xml file
    :param xml_file_path: Path object to the xml file
    :return: a list of the bug reports as a dictionary
    """
    try:
        file = open(xml_file_path, 'r')
        content = file.read().encode()

        # Removes garbage binary characters to avoid parsing error
        content = re.sub(rb'[^\x09\x0A\x0D\x20-\x7E]', b'', content)
        file.close()

    except FileNotFoundError:
        return None

    xml_tree = ElementTree.fromstring(content)
    bug_reports = []
    for table in xml_tree.findall("./database/"):
        table_dict = {
            entry.attrib["name"]: entry.text for entry in table
        }
        bug_reports.append(table_dict)

    return pd.DataFrame(bug_reports)


def retrieve_parent_commit(
        repo: Repo,
        commit_sha: str,
        commit_folder_path: str
):
    """
    Retrieves all files at a repo's commit's parent commit
    and save to the given path
    :param repo: Repository object
    :param commit_sha: sha key of the fixed commit
    :param commit_folder_path: the folder to save the code data
    """

    # Return if the commit has already been processed
    if os.path.exists(commit_folder_path):
        return

    fixed_commit = repo.commit(commit_sha)
    previous_commit = fixed_commit.parents[0]

    changed_files = [item.a_path for item in previous_commit.diff(fixed_commit)]

    # repo.head.reference = previous_commit
    # repo.head.reset(index=True, working_tree=True)

    # shutil.copytree(repo_path, folder_path)


def process_files():
    """
    Processes all the files and save data
    """
    for file, git_url in project_repo_mapping.items():
        # Process each of the xml files and their respective git repo
        project_name = file.split('.')[0]
        print(f"Processing project xml: {project_name}")
        reports = retrieve_bug_reports(os.path.join(DATA_FOLDER_PATH, file))

        if reports is None:
            print(f"Failed to parse {file}")
            continue

        save_data_path = os.path.join(os.getcwd(), project_name)

        print(f"Cloning from {project_name}")
        repo_path = 'temp_repo'
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        repo = Repo.clone_from(git_url, repo_path)
        print("Cloning successful\nProcessing commits...")

        def process_associated_path(commit_sha):
            if not commit_sha:
                return ""

            output_folder = os.path.join(save_data_path, commit_sha + "~1")
            try:
                retrieve_parent_commit(repo, commit_sha, output_folder)
            except Exception as e:
                print("Failed to retrieve commit {}".format(commit_sha))

            return output_folder

        # Process the associated source file input path to each bug report
        reports["input_path"] = [process_associated_path(commit) for commit in reports["commit"]]

        # Save the dataframe to csv
        if not os.path.exists(save_data_path):
            os.makedirs(save_data_path)

        saved_csv_path = os.path.join(save_data_path, "bug_report_data.csv")
        reports.to_csv(saved_csv_path, index=False)
        print(f"Saved to {saved_csv_path}")

        repo.close()
        print(f"Repository: {project_name} closed")

        shutil.rmtree(repo_path)


process_files()
