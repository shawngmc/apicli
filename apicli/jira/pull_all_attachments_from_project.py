import argparse
import json
import logging
import os

from jira import JIRA

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
_LOGGER.addHandler(console_handler)

def _parseargs():
    parser = argparse.ArgumentParser(description='Get all attachments from a specific jira project.')
    parser.add_argument('project', help="project key (for example DEV as in DEV-####)")
    parser.add_argument('out_path', help="folder to output to")
    args = parser.parse_args()
    return args

def _read_creds():
    with open("creds.json", "r", encoding = "utf-8") as cred_file:
        creds = json.loads(cred_file.read())
    if creds['username'] != '' and creds['password'] != '':
        _LOGGER.info("Credentials loaded...")
        return creds
    else:
        _LOGGER.info("Check creds file...")
        exit()


def download_attachment(folder, entry):
    if not os.path.exists(folder):
        os.makedirs(folder)
    out_path = os.path.join(folder, entry.filename)
    # in_file = entry.iter_content()
    with open(out_path, 'wb') as out_file:
        out_file.write(entry.get())

def main():
    """Download attachments for a project"""
    args = _parseargs()
    creds = _read_creds()

    # Initialize JIRA API
    jira = JIRA(
        basic_auth=(creds['username'], creds['password']),
        server=creds['host']
    )

    _LOGGER.info(f"Getting issues for project {args.project}...")
    issues = jira.search_issues(f'project = "{args.project}"')
    for issue in issues:
        _LOGGER.info(f"Getting attachments for issue {issue.key}...")
        issue_details = jira.issue(issue.id)
        attachment_list = issue_details.fields.attachment
        folder = os.path.join(args.out_path, issue.key)
        for attachment_entry in attachment_list:
            _LOGGER.info(f"  Downloading attachment {attachment_entry.filename} for issue {issue.key}...")
            download_attachment(folder, attachment_entry)


main()
