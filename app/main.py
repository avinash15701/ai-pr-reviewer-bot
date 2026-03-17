from fastapi import FastAPI, Request
from app.github_service import get_pr_files, comment_on_pr
from app.reviewer import review_code
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


@app.get("/")
def home():
    return {"message": "AI PR Reviewer Running"}


@app.post("/webhook")
async def github_webhook(request: Request):
    """
    GitHub Webhook handler for pull request events.
    Automatically reviews Python files in PRs using AI and comments back on the PR.
    """

    try:
        payload = await request.json()
    except Exception as e:
        logging.error(f"Failed to parse JSON payload: {e}")
        return {"status": "Invalid JSON payload"}

    action = payload.get("action")

    logging.info(f"Webhook payload received: action={action}")

    # Only process PR open or new commits
    if action not in ["opened", "synchronize"]:
        logging.info(f"Ignored action: {action}")
        return {"status": f"Ignored action: {action}"}

    repo = payload.get("repository", {})
    pr = payload.get("pull_request", {})

    repo_name = repo.get("full_name")
    pr_number = pr.get("number")

    if not repo_name or not pr_number:
        logging.warning("Missing repository or PR number in payload")
        return {"status": "Missing repository or PR number"}

    logging.info(f"Processing PR #{pr_number} in repo {repo_name}")

    try:
        files = get_pr_files(repo_name, pr_number)
    except Exception as e:
        logging.error(f"Failed to fetch PR files: {e}")
        return {"status": "Failed to fetch PR files"}

    review_comments = []

    for file in files:
        filename = file.get("filename")
        patch = file.get("patch")

        logging.info(f"Detected file: {filename}")

        if filename and filename.endswith(".py"):

            if not patch:
                logging.info(f"Skipping {filename} (no patch available)")
                continue

            try:
                # Extract only added lines from patch
                clean_code = "\n".join(
                    line[1:] for line in patch.split("\n") if line.startswith("+")
                )

                ai_review = review_code(clean_code)

                if ai_review.strip():
                    review_comments.append(f"### File: {filename}\n{ai_review}\n")

            except Exception as e:
                logging.error(f"AI review failed for {filename}: {e}")

    final_comment = "\n".join(review_comments)

    if final_comment:
        try:
            comment_on_pr(repo_name, pr_number, final_comment)
            logging.info(f"Posted AI review on PR #{pr_number}")
        except Exception as e:
            logging.error(f"Failed to post comment on PR #{pr_number}: {e}")
            return {"status": "Failed to post comment"}

    else:
        logging.info(f"No Python changes to review on PR #{pr_number}")

    return {"status": "Webhook processed successfully"}