"""AI engine: one primary provider (Gemini) plus a fallback (Groq).

Both a blocking :func:`generate` and an incremental :func:`stream` are
exposed.  Provider SDKs are imported once at module load; if an SDK is not
installed the corresponding provider is simply reported as unavailable
instead of raising at call time.
"""

from __future__ import annotations

import os
from collections.abc import Iterator

from dotenv import load_dotenv

try:  # Optional dependency: pip install google-genai
    from google import genai
    from google.genai import types as genai_types
except ImportError:  # pragma: no cover - depends on local environment
    genai = None
    genai_types = None

try:  # Optional dependency: pip install openai
    from openai import OpenAI
except ImportError:  # pragma: no cover - depends on local environment
    OpenAI = None

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


class EngineError(RuntimeError):
    """Raised when every configured provider fails."""


# ---------------------------------------------------------------------------
# Provider availability
# ---------------------------------------------------------------------------


def gemini_ready() -> bool:
    """Return True when the Gemini SDK is installed and a key is present."""
    return bool(genai is not None and GEMINI_API_KEY)


def groq_ready() -> bool:
    """Return True when the OpenAI SDK is installed and a key is present."""
    return bool(OpenAI is not None and GROQ_API_KEY)


def provider_status() -> list[dict]:
    """Return a small summary of each provider, for display in the UI."""
    return [
        {"name": "Gemini", "model": GEMINI_MODEL, "ready": gemini_ready()},
        {"name": "Groq", "model": GROQ_MODEL, "ready": groq_ready()},
    ]


def _no_provider_error() -> EngineError:
    return EngineError(
        "No AI provider is configured. Add GEMINI_API_KEY or GROQ_API_KEY "
        "to your .env file, then restart the app."
    )


# ---------------------------------------------------------------------------
# Internal provider calls
# ---------------------------------------------------------------------------


def _gemini_client():
    if genai is None or genai_types is None:
        raise EngineError(
            "The google-genai package is not installed. "
            "Run: pip install -r requirements.txt"
        )
    return genai.Client(api_key=GEMINI_API_KEY)


def _gemini_config(temperature: float):
    return genai_types.GenerateContentConfig(temperature=temperature)


def _gemini_generate(system_prompt: str, user_prompt: str,
                     temperature: float) -> str:
    client = _gemini_client()
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=f"{system_prompt}\n\n{user_prompt}",
        config=_gemini_config(temperature),
    )
    return response.text or ""


def _gemini_stream(system_prompt: str, user_prompt: str,
                   temperature: float) -> Iterator[str]:
    client = _gemini_client()
    chunks = client.models.generate_content_stream(
        model=GEMINI_MODEL,
        contents=f"{system_prompt}\n\n{user_prompt}",
        config=_gemini_config(temperature),
    )
    for chunk in chunks:
        if chunk.text:
            yield chunk.text


def _groq_client():
    if OpenAI is None:
        raise EngineError(
            "The openai package is not installed. "
            "Run: pip install -r requirements.txt"
        )
    return OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)


def _groq_messages(system_prompt: str, user_prompt: str) -> list[dict]:
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _groq_generate(system_prompt: str, user_prompt: str,
                   temperature: float) -> str:
    response = _groq_client().chat.completions.create(
        model=GROQ_MODEL,
        messages=_groq_messages(system_prompt, user_prompt),
        temperature=temperature,
    )
    return response.choices[0].message.content or ""


def _groq_stream(system_prompt: str, user_prompt: str,
                 temperature: float) -> Iterator[str]:
    response = _groq_client().chat.completions.create(
        model=GROQ_MODEL,
        messages=_groq_messages(system_prompt, user_prompt),
        temperature=temperature,
        stream=True,
    )
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate(system_prompt: str, user_prompt: str,
             temperature: float = 0.7) -> str:
    """Return a complete response, trying Gemini first and Groq second.

    Raises:
        EngineError: if no provider is configured, or all of them failed.
    """
    if not gemini_ready() and not groq_ready():
        raise _no_provider_error()

    failures: list[str] = []

    if gemini_ready():
        try:
            return _gemini_generate(system_prompt, user_prompt, temperature)
        except Exception as exc:  # noqa: BLE001 - SDK errors are untyped
            failures.append(f"Gemini: {exc}")

    if groq_ready():
        try:
            return _groq_generate(system_prompt, user_prompt, temperature)
        except Exception as exc:  # noqa: BLE001 - SDK errors are untyped
            failures.append(f"Groq: {exc}")

    raise EngineError(" | ".join(failures) or "All providers failed.")


def stream(system_prompt: str, user_prompt: str,
           temperature: float = 0.7) -> Iterator[str]:
    """Yield response chunks, trying Gemini first and Groq second.

    Once a provider has emitted its first chunk the engine stays with it: a
    later failure is raised rather than silently restarted on the fallback,
    which would duplicate text already shown to the user.

    Raises:
        EngineError: if no provider is configured, or all of them failed.
    """
    if not gemini_ready() and not groq_ready():
        raise _no_provider_error()

    failures: list[str] = []
    providers = (
        (gemini_ready(), _gemini_stream, "Gemini"),
        (groq_ready(), _groq_stream, "Groq"),
    )

    for ready, producer, label in providers:
        if not ready:
            continue

        emitted = False
        try:
            for chunk in producer(system_prompt, user_prompt, temperature):
                emitted = True
                yield chunk
            return
        except Exception as exc:  # noqa: BLE001 - SDK errors are untyped
            if emitted:
                raise EngineError(
                    f"{label} stopped mid-response: {exc}"
                ) from exc
            failures.append(f"{label}: {exc}")

    raise EngineError(" | ".join(failures) or "All providers failed.")


# ---------------------------------------------------------------------------
# Manual smoke test:  python engine.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    for provider in provider_status():
        state = "ready" if provider["ready"] else "not configured"
        print(f"{provider['name']:8s} {provider['model']:28s} {state}")

    print("\nStreaming test:\n")
    try:
        for piece in stream(
            "You are a helpful assistant.",
            "Say hello in one short sentence.",
            temperature=0.3,
        ):
            print(piece, end="", flush=True)
        print("\n\nDone.")
    except EngineError as error:
        print(f"Engine error: {error}")
