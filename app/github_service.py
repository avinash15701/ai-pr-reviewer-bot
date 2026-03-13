from github import Github
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def get_repo(repo_name):

    g = Github(GITHUB_TOKEN)

    repo = g.get_repo(repo_name)

    return repo


def get_open_prs(repo_name):

    repo = get_repo(repo_name)

    prs = repo.get_pulls(state="open")

    pr_data = []

    for pr in prs:

        pr_data.append({
            "number": pr.number,
            "title": pr.title,
            "author": pr.user.login
        })

    return  pr_data


def get_pr_files(repo_name, pr_number):

    repo = get_repo(repo_name)

    pr = repo.get_pull(pr_number)

    files = pr.get_files()

    file_changes = []

    for file in files:

        file_changes.append({
            "filename": file.filename,
            "patch": file.patch
        })

    return file_changes