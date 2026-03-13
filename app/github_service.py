from github import Github
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

g = Github(GITHUB_TOKEN)


def get_repo(repo_name):
    return g.get_repo(repo_name)


def get_open_prs(repo_name):

    repo = get_repo(repo_name)
    prs = repo.get_pulls(state="open")

    pr_list = []

    for pr in prs:
        pr_list.append({
            "number": pr.number,
            "title": pr.title,
            "author": pr.user.login
        })

    return pr_list


def get_pr_files(repo_name, pr_number):

    repo = get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    files = []

    for file in pr.get_files():
        files.append({
            "filename": file.filename,
            "patch": file.patch
        })

    return files


def comment_on_pr(repo_name, pr_number, comment):

    repo = get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    pr.create_issue_comment(comment)