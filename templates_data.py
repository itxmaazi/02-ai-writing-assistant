"""Writing templates: pre-built prompts with fields the user fills in.

Every ``prompt_builder`` reads its fields with ``.get`` so a blank or
missing field degrades gracefully instead of raising ``KeyError``.
"""

from __future__ import annotations

TONE_SHORT = ["Professional", "Casual", "Friendly", "Humorous", "Persuasive"]

LENGTHS = [
    "Short (300-500 words)",
    "Medium (800-1200 words)",
    "Long (1500-2500 words)",
]


def _blog(f: dict) -> str:
    return (
        f"Write a blog post about: {f.get('topic', '')}\n"
        f"Target audience: {f.get('audience') or 'General readers'}\n"
        f"Tone: {f.get('tone', 'Casual')}\n"
        f"Length: {f.get('length', LENGTHS[1])}\n\n"
        "Include a catchy title, an introduction, subheadings and a "
        "conclusion."
    )


def _email(f: dict) -> str:
    return (
        "Write an email with the following details:\n"
        f"Purpose: {f.get('purpose', '')}\n"
        f"Recipient: {f.get('recipient') or 'the reader'}\n"
        f"Tone: {f.get('tone', 'Professional')}\n"
        f"Key points to include:\n{f.get('key_points', '')}\n\n"
        "Write the complete email with a subject line, greeting, body "
        "and sign-off."
    )


def _essay(f: dict) -> str:
    thesis = f.get("thesis") or "Develop a strong thesis from the topic"
    return (
        f"Write a {f.get('type', 'Argumentative')} essay about: "
        f"{f.get('topic', '')}\n"
        f"Length: {f.get('length', LENGTHS[1])}\n"
        f"Thesis statement: {thesis}\n\n"
        "Include an introduction with the thesis, body paragraphs with "
        "evidence, and a conclusion. Use an academic writing style."
    )


def _story(f: dict) -> str:
    return (
        "Write a short story with these details:\n"
        f"Genre: {f.get('genre', 'Fantasy')}\n"
        f"Setting: {f.get('setting', '')}\n"
        f"Main characters: {f.get('characters', '')}\n"
        f"Plot idea: {f.get('idea', '')}\n\n"
        "Give it a clear beginning, middle and end. Use vivid "
        "description and natural dialogue."
    )


def _social(f: dict) -> str:
    return (
        f"Write a {f.get('platform', 'Twitter/X')} post about: "
        f"{f.get('topic', '')}\n"
        f"Tone: {f.get('tone', 'Casual')}\n"
        f"Goal: {f.get('goal', 'Get engagement')}\n\n"
        "Add hashtags if they suit the platform, and stay within the "
        "platform's character limits."
    )


def _resume(f: dict) -> str:
    metrics = f.get("metrics") or "Use realistic placeholder metrics"
    return (
        f"Write 5 strong resume bullet points for a "
        f"{f.get('job_title', 'professional')} role.\n"
        f"Achievement: {f.get('achievement', '')}\n"
        f"Measurable results: {metrics}\n\n"
        "Use the STAR method (Situation, Task, Action, Result). Start "
        "each bullet with a strong action verb and include numbers "
        "where possible."
    )


def _report(f: dict) -> str:
    return (
        "Write a professional business report:\n"
        f"Topic: {f.get('topic', '')}\n"
        f"Audience: {f.get('audience') or 'Senior management'}\n"
        f"Key data and findings:\n{f.get('data_points', '')}\n"
        f"Recommendations:\n{f.get('recommendations', '')}\n\n"
        "Use this structure: Executive Summary, Introduction, Findings, "
        "Analysis, Recommendations, Conclusion. Keep the tone "
        "professional and data-driven."
    )


def _techdoc(f: dict) -> str:
    return (
        "Write technical documentation:\n"
        f"Subject: {f.get('subject', '')}\n"
        f"Audience level: {f.get('audience_level', 'Intermediate')}\n"
        f"Format: {f.get('format', 'Tutorial / How-to')}\n"
        f"Key details:\n{f.get('details', '')}\n\n"
        "Use clear, precise language. Include code examples where "
        "relevant, with proper headings, bullets and numbered steps."
    )


TEMPLATES: dict[str, dict] = {
    "blog_post": {
        "name": "Blog Post",
        "icon": "📰",
        "description": "Write an engaging blog post on any topic",
        "tool": "write",
        "prompt_builder": _blog,
        "fields": [
            {"name": "topic", "label": "Topic", "type": "text",
             "placeholder": "10 tips for better sleep"},
            {"name": "audience", "label": "Target audience", "type": "text",
             "placeholder": "Young professionals"},
            {"name": "tone", "label": "Tone", "type": "select",
             "options": TONE_SHORT, "default": "Casual"},
            {"name": "length", "label": "Length", "type": "select",
             "options": LENGTHS, "default": LENGTHS[1]},
        ],
    },
    "email": {
        "name": "Email",
        "icon": "📧",
        "description": "Draft a professional or casual email",
        "tool": "write",
        "prompt_builder": _email,
        "fields": [
            {"name": "purpose", "label": "Purpose", "type": "text",
             "placeholder": "Follow up on a job application"},
            {"name": "recipient", "label": "Recipient", "type": "text",
             "placeholder": "Hiring manager"},
            {"name": "tone", "label": "Tone", "type": "select",
             "options": ["Professional", "Formal", "Friendly", "Casual"],
             "default": "Professional"},
            {"name": "key_points", "label": "Key points",
             "type": "textarea",
             "placeholder": "Thank them, mention my availability"},
        ],
    },
    "essay": {
        "name": "Essay",
        "icon": "📄",
        "description": "Write a structured academic essay",
        "tool": "write",
        "prompt_builder": _essay,
        "fields": [
            {"name": "topic", "label": "Essay topic", "type": "text",
             "placeholder": "The impact of AI on education"},
            {"name": "type", "label": "Essay type", "type": "select",
             "options": ["Argumentative", "Expository", "Narrative",
                         "Descriptive", "Compare & Contrast"],
             "default": "Argumentative"},
            {"name": "length", "label": "Length", "type": "select",
             "options": LENGTHS, "default": LENGTHS[1]},
            {"name": "thesis", "label": "Thesis (optional)",
             "type": "textarea",
             "placeholder": "AI will enhance rather than replace teachers"},
        ],
    },
    "story": {
        "name": "Short Story",
        "icon": "📖",
        "description": "Write a creative short story",
        "tool": "write",
        "prompt_builder": _story,
        "fields": [
            {"name": "genre", "label": "Genre", "type": "select",
             "options": ["Fantasy", "Sci-Fi", "Mystery", "Romance",
                         "Horror", "Thriller", "Comedy", "Drama"],
             "default": "Fantasy"},
            {"name": "setting", "label": "Setting", "type": "text",
             "placeholder": "A floating city in 2150"},
            {"name": "characters", "label": "Main characters",
             "type": "text",
             "placeholder": "A young detective and her AI partner"},
            {"name": "idea", "label": "Plot idea", "type": "textarea",
             "placeholder": "Crimes are predicted before they happen"},
        ],
    },
    "social_media": {
        "name": "Social Post",
        "icon": "📱",
        "description": "Create posts for X, LinkedIn, Instagram and more",
        "tool": "write",
        "prompt_builder": _social,
        "fields": [
            {"name": "platform", "label": "Platform", "type": "select",
             "options": ["Twitter/X", "LinkedIn", "Instagram", "Facebook",
                         "Reddit"],
             "default": "Twitter/X"},
            {"name": "topic", "label": "Topic", "type": "text",
             "placeholder": "Sharing a project I built"},
            {"name": "tone", "label": "Tone", "type": "select",
             "options": ["Professional", "Casual", "Humorous",
                         "Inspirational", "Educational"],
             "default": "Casual"},
            {"name": "goal", "label": "Goal", "type": "select",
             "options": ["Get engagement", "Share knowledge",
                         "Promote something", "Start a discussion",
                         "Entertain"],
             "default": "Get engagement"},
        ],
    },
    "resume_bullet": {
        "name": "Resume Bullets",
        "icon": "💼",
        "description": "Write powerful, metric-driven resume bullets",
        "tool": "write",
        "prompt_builder": _resume,
        "fields": [
            {"name": "job_title", "label": "Job title", "type": "text",
             "placeholder": "Software Developer"},
            {"name": "achievement", "label": "What you did",
             "type": "textarea",
             "placeholder": "Built an automated reporting system"},
            {"name": "metrics", "label": "Results / numbers",
             "type": "text",
             "placeholder": "Cut reporting time by 60%"},
        ],
    },
    "business_report": {
        "name": "Business Report",
        "icon": "📊",
        "description": "Write a structured business or project report",
        "tool": "write",
        "prompt_builder": _report,
        "fields": [
            {"name": "topic", "label": "Report topic", "type": "text",
             "placeholder": "Q3 sales performance review"},
            {"name": "audience", "label": "Audience", "type": "text",
             "placeholder": "Senior management"},
            {"name": "data_points", "label": "Key data / findings",
             "type": "textarea",
             "placeholder": "Revenue up 15%, churn up 3%"},
            {"name": "recommendations", "label": "Recommendations",
             "type": "textarea",
             "placeholder": "Invest in customer retention"},
        ],
    },
    "technical_doc": {
        "name": "Technical Doc",
        "icon": "🔧",
        "description": "Write clear technical documentation",
        "tool": "write",
        "prompt_builder": _techdoc,
        "fields": [
            {"name": "subject", "label": "Subject", "type": "text",
             "placeholder": "API authentication flow"},
            {"name": "audience_level", "label": "Audience level",
             "type": "select",
             "options": ["Beginner", "Intermediate", "Advanced", "Expert"],
             "default": "Intermediate"},
            {"name": "format", "label": "Format", "type": "select",
             "options": ["Tutorial / How-to", "API Reference", "README",
                         "Architecture Doc", "Troubleshooting Guide"],
             "default": "Tutorial / How-to"},
            {"name": "details", "label": "Key details", "type": "textarea",
             "placeholder": "OAuth2, API key, 100 req/min rate limit"},
        ],
    },
}
