from fastapi import FastAPI, Request
from app.github_service import get_open_prs, get_pr_files, comment_on_pr
from app.reviewer import review_code
import logging

app = FastAPI()

# Optional: log webhook payloads for debugging
logging.basicConfig(level=logging.INFO)

@app.get("/")
def home():
    return {"message": "AI PR Reviewer Running"}


@app.post("/webhook")
async def github_webhook(request: Request):
    try:
        payload = await request.json()
    except Exception:
        return {"status": "Invalid JSON payload"}

    # Log payload for debugging
    logging.info(f"Webhook payload received: {payload}")

    # Only process PR events
    action = payload.get("action")
    if action not in ["opened", "synchronize"]:
        return {"status": f"Ignored action: {action}"}

    # Safely get repository and PR number
    repo = payload.get("repository", {})
    pr = payload.get("pull_request", {})

    repo_name = repo.get("full_name")
    pr_number = pr.get("number")

    if not repo_name or not pr_number:
        return {"status": "Missing repository or PR number"}

    # Get files from the PR
    files = get_pr_files(repo_name, pr_number)
    review_comments = []

    for file in files:
        filename = file.get("filename")
        patch = file.get("patch")

        # Only review Python files with code changes
        if not filename.endswith(".py") or patch is None:
            continue

        ai_review = review_code(patch)
        review_comments.append(f"### File: {filename}\n{ai_review}\n")

        

    # Combine all file reviews
    final_comment = "\n".join(review_comments)

    # Post comment on PR if there are reviews
    if final_comment:
        comment_on_pr(repo_name, pr_number, final_comment)
        logging.info(f"Posted AI review on PR #{pr_number}")
    else:
        logging.info(f"No Python changes to review on PR #{pr_number}")

    return {"status": "Webhook processed"}