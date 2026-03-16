import ollama


def review_code(code):

    prompt = f"""
You are a senior software engineer reviewing a GitHub pull request.

Review the code carefully and identify:
1. Bugs
2. Performance issues
3. Security issues
4. Code quality problems

If the code is correct and no improvements are needed, respond with:
"No issues found. The code looks good."

Provide specific feedback only when a real issue exists.

Code:
{code}
"""

    response = ollama.chat(
        model="deepseek-coder",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]