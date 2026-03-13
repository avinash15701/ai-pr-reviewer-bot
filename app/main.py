from fastapi import FastAPI, Request
from app.github_service import get_open_prs, get_pr_files, comment_on_pr
from app.reviewer import review_code

app = FastAPI()


@app.get("/")
def home():
    return {"message": "AI PR Reviewer Running"}


@app.post("/webhook")
async def github_webhook(request: Request):

    payload = await request.json()

    # Trigger only when PR is opened
    if payload["action"] == "opened":

        repo_name = payload["repository"]["full_name"]
        pr_number = payload["pull_request"]["number"]

        files = get_pr_files(repo_name, pr_number)

        review_comments = []

        for file in files:

            filename = file.get("filename")
            patch = file.get("patch")

            if not filename.endswith(".py"):
                continue

            if patch is None:
                continue

            ai_review = review_code(patch)

            review_comments.append(
                f"### File: {filename}\n{ai_review}\n"
            )

        final_comment = "\n".join(review_comments)

        comment_on_pr(repo_name, pr_number, final_comment)

    return {"status": "Webhook processed"}