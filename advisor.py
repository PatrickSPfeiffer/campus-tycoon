import json
import urllib.request


def ask_openrouter(prompt, api_key):
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is empty.")

    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(
            {
                "model": "openrouter/free",
                "messages": [{"role": "user", "content": prompt}],
            }
        ).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        answer = json.loads(response.read().decode("utf-8"))
    return answer["choices"][0]["message"]["content"]
