"""DeepSeek API client wrapper (OpenAI-compatible)."""
from openai import OpenAI
from config import Config


def get_client():
    """Get configured DeepSeek client."""
    return OpenAI(
        api_key=Config.DEEPSEEK_API_KEY,
        base_url=Config.DEEPSEEK_BASE_URL,
    )


def chat(prompt, system_prompt=None, model="deepseek-chat", stream=True):
    """Send a chat completion request to DeepSeek.

    Returns the full response content as a string.
    """
    client = get_client()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        top_p=0.8,
        stream=stream,
    )

    result = ""
    for chunk in response:
        delta = chunk.choices[0].delta
        if hasattr(delta, "content") and delta.content:
            result += delta.content

    return result
