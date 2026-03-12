import ollama


def review_code(code):

    prompt = f"""
You are a senior software engineer.

Review the following code changes from a pull request.
Suggest improvements, bugs, and best practices.

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