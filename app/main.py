from fastapi import FastAPI
from app.github_service import get_open_prs, get_pr_files
from app.reviewer import review_code

app = FastAPI()


@app.get("/")
def home():
    return {"message": "AI PR Reviewer Running"}


@app.get("/prs")
def get_prs(repo_name: str):
    prs = get_open_prs(repo_name)

    return {
        "repository": repo_name,
        "open_prs": prs
    }


@app.post("/review-pr")
def review_pr(repo_name: str, pr_number: int):

    files = get_pr_files(repo_name, pr_number)

    reviews = []

    for file in files:

        code_changes = file["patch"]

        ai_review = review_code(code_changes)

        reviews.append({
            "file_name": file["filename"],
            "review": ai_review
        })

    return {
        "repository": repo_name,
        "pr_number": pr_number,
        "reviews": reviews
    }