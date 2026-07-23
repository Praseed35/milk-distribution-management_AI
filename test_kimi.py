import requests

api_key = "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"   # Paste your real key here temporarily

response = requests.post(
    "https://integrate.api.nvidia.com/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    },
    json={
        "model": "nvidia/nemotron-3-ultra-550b-a55b",
        "messages": [
            {
                "role": "user",
                "content": "Say OK"
            }
        ]
    }
)

print(response.status_code)
print(response.text)