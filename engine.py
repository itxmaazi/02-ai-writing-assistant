# engine.py
# ============================================================
# AI ENGINE — Simple, Fast, Reliable
# ============================================================
# One primary provider (Gemini) + one fallback (Groq).
# Different temperatures for different writing tasks.
# Streaming output — text appears word by word.
# ============================================================

import os
import time
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GEMINI_MODEL = "gemini-2.0-flash"
GROQ_MODEL = "llama-3.3-70b-versatile"


# ============================================================
# NON-STREAMING (for tools that need the full response at once)
# ============================================================

def generate(system_prompt, user_prompt, temperature=0.7):
    """
    Sends a prompt to Gemini. Falls back to Groq on failure.
    Returns the complete response as a string.

    Args:
        system_prompt: instructions for the AI (what role to play)
        user_prompt: the actual content/request
        temperature: 0.0 (precise) to 1.0 (creative)

    Returns:
        str: the AI's response
    """
    # Try Gemini first
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
            ),
        )
        return response.text

    except Exception:
        pass  # Fall through to Groq

    # Fallback to Groq
    try:
        from openai import OpenAI

        client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Error: Both providers failed. {str(e)}"


# ============================================================
# STREAMING (for real-time text output)
# ============================================================

def stream(system_prompt, user_prompt, temperature=0.7):
    """
    Streams a response word by word from Gemini.
    Falls back to Groq on failure.
    Yields text chunks as they arrive.

    Usage:
        for chunk in stream("You are...", "Write about...", 0.7):
            print(chunk, end="", flush=True)

    Args:
        system_prompt: instructions for the AI
        user_prompt: the actual content/request
        temperature: 0.0 to 1.0

    Yields:
        str: text chunks as they arrive
    """
    # Try Gemini streaming
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        for chunk in client.models.generate_content_stream(
            model=GEMINI_MODEL,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
            ),
        ):
            if chunk.text:
                yield chunk.text
        return  # Success — don't try Groq

    except Exception:
        pass  # Fall through to Groq

    # Fallback to Groq streaming
    try:
        from openai import OpenAI

        client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

        response_stream = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            stream=True,
        )

        for chunk in response_stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as e:
        yield f"Error: Both providers failed. {str(e)}"


# ============================================================
# QUICK TEST
# ============================================================

if __name__ == "__main__":
    print("Testing engine...\n")

    result = generate(
        "You are a helpful assistant.",
        "Say hello in one sentence.",
        temperature=0.3,
    )
    print(f"Generate: {result}\n")

    print("Stream: ", end="")
    for chunk in stream(
        "You are a helpful assistant.",
        "Count from 1 to 5 with a word after each number.",
        temperature=0.3,
    ):
        print(chunk, end="", flush=True)
    print("\n\nDone.")