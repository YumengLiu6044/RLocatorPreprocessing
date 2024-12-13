from git import Repo
import pandas as pd
import os
from xml.etree import ElementTree
import re
from zipfile import ZipFile, ZIP_DEFLATED
from tqdm import tqdm

DATA_FOLDER_PATH = "data/dataset"
project_repo_mapping = {
    'Birt.xml': "birt_repo",
    'Eclipse_Platform_UI.xml': "eclipse_ui_repo",
    'AspectJ.xml': "aspectj_repo",
    'JDT.xml': "jdt_repo",
    'SWT.xml': "swt_repo",
    'Tomcat.xml': "tomcat_repo"
}
repo_paths_mapping = {
    'birt_repo': "https://github.com/eclipse-birt/birt.git",
    'eclipse_ui_repo': "https://github.com/eclipse-platform/eclipse.platform.ui.git",
    'aspectj_repo': "https://github.com/eclipse-aspectj/aspectj.git",
    'jdt_repo': "https://github.com/eclipse-jdt/eclipse.jdt.ui.git",
    'swt_repo': "https://github.com/eclipse-platform/eclipse.platform.swt.git",
    'tomcat_repo': "https://github.com/apache/tomcat.git"
}

# Clone all the repositories into respective folders
for path_name, repo_url in repo_paths_mapping.items():
    repo_path = os.path.join(os.getcwd(), path_name)
    if os.path.exists(repo_path):
        print(f"Repository: {path_name} exists")
        continue
    else:
        print(f"Cloning repository: {path_name}")
        os.mkdir(repo_path)
        try:
            repo = Repo.clone_from(repo_url, repo_path)
            repo.close()
            print("Cloning success")
        except Exception as e:
            print(f"Cloning failed:\n{e}")


def retrieve_bug_reports(xml_file_path: str) -> pd.DataFrame | None:
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


def archive_files(output_path, input_paths):
    if os.path.exists(output_path):
        return

    with ZipFile(output_path, "w", ZIP_DEFLATED) as zipped_file:
        for path in input_paths:
            zipped_file.write(path, arcname=path.replace('/', '-'))


def retrieve_parent_commit(
        repo: Repo,
        commit_sha: str,
        commit_folder_path: str,
        repo_path: str
):
    """
    Retrieves all files at a repo's commits' parent commit
    and save to the given path
    """

    # Return if the commit has already been processed
    if os.path.exists(commit_folder_path):
        return

    fixed_commit = repo.commit(commit_sha)
    previous_commit = fixed_commit.parents[0]

    archiving_files = {os.path.join(repo_path, item.a_path)
                       for item in previous_commit.diff(fixed_commit)
                       if item.change_type != 'A'}

    repo.head.reference = previous_commit
    repo.head.reset(index=True, working_tree=True)

    for root, _, files in os.walk(repo_path):
        for file in files:
            full_path = os.path.join(repo_path, root, file)
            if file.endswith(".java") and full_path not in archiving_files:
                archiving_files.add(full_path)

    archive_files(commit_folder_path, archiving_files)


def process_files():
    """
    Processes all the files and save data
    """
    for file, repo_path in tqdm(project_repo_mapping.items(), desc=f"Processing project"):
        # Process each of the xml files and their respective git repo
        project_name = file.split('.')[0]
        print(f"Processing project: {project_name}")
        reports = retrieve_bug_reports(os.path.join(DATA_FOLDER_PATH, file))

        if reports is None:
            print(f"Failed to parse {file}")
            continue

        save_data_path = os.path.join(os.getcwd(), project_name)

        if not os.path.exists(save_data_path):
            os.makedirs(save_data_path)

        print(f"Processing repository: {repo_path}")
        repo = Repo(os.path.join(os.getcwd(), repo_path))

        def process_associated_path(commit_sha):
            if not commit_sha:
                return ""

            output_folder = os.path.join(save_data_path, commit_sha + "~1")
            try:
                retrieve_parent_commit(repo, commit_sha, output_folder, os.path.join(os.getcwd(), repo_path))
            except Exception as e:
                print(e)
                print("Failed to retrieve commit {}".format(commit_sha))
            finally:
                return output_folder

        # Process the associated source file input path to each bug report
        reports["input_path"] = [
            process_associated_path(commit) for commit in tqdm(reports["commit"], desc="Processing commits")
        ]

        # Save the dataframe to csv
        saved_csv_path = os.path.join(save_data_path, "bug_report_data.csv")
        reports.to_csv(saved_csv_path, index=False)
        print(f"Saved to {saved_csv_path}")

        repo.close()
        print(f"Repository: {project_name} closed")


process_files()
