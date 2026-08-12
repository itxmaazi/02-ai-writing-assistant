# templates_data.py
# ============================================================
# WRITING TEMPLATES
# ============================================================
# Pre-built prompts for common writing tasks.
# Each template has fields the user fills out.
# ============================================================

TEMPLATES = {
    "blog_post": {
        "name": "Blog Post",
        "icon": "📰",
        "description": "Write an engaging blog post on any topic",
        "tool": "write",
        "fields": [
            {"name": "topic", "label": "Topic", "type": "text", "placeholder": "e.g., 10 Tips for Better Sleep"},
            {"name": "audience", "label": "Target Audience", "type": "text", "placeholder": "e.g., Young professionals"},
            {"name": "tone", "label": "Tone", "type": "select", "options": [
                "Professional", "Casual", "Friendly", "Humorous", "Persuasive"
            ], "default": "Casual"},
            {"name": "length", "label": "Length", "type": "select", "options": [
                "Short (300-500 words)", "Medium (800-1200 words)", "Long (1500-2500 words)"
            ], "default": "Medium (800-1200 words)"},
        ],
        "prompt_builder": lambda fields: (
            f"Write a blog post about: {fields['topic']}\n"
            f"Target audience: {fields['audience']}\n"
            f"Tone: {fields['tone']}\n"
            f"Length: {fields['length']}\n\n"
            f"Include a catchy title, introduction, subheadings, and conclusion."
        ),
    },

    "email": {
        "name": "Email",
        "icon": "📧",
        "description": "Draft a professional or casual email",
        "tool": "write",
        "fields": [
            {"name": "purpose", "label": "Purpose of Email", "type": "text", "placeholder": "e.g., Follow up on job application"},
            {"name": "recipient", "label": "Recipient", "type": "text", "placeholder": "e.g., Hiring manager, Client, Friend"},
            {"name": "tone", "label": "Tone", "type": "select", "options": [
                "Professional", "Formal", "Friendly", "Casual"
            ], "default": "Professional"},
            {"name": "key_points", "label": "Key Points to Include", "type": "textarea", "placeholder": "e.g., Thank them for the interview, mention my availability"},
        ],
        "prompt_builder": lambda fields: (
            f"Write an email with the following details:\n"
            f"Purpose: {fields['purpose']}\n"
            f"Recipient: {fields['recipient']}\n"
            f"Tone: {fields['tone']}\n"
            f"Key points to include:\n{fields.get('key_points', '')}\n\n"
            f"Write the complete email with subject line, greeting, body, and sign-off."
        ),
    },

    "essay": {
        "name": "Essay",
        "icon": "📄",
        "description": "Write a structured academic essay",
        "tool": "write",
        "fields": [
            {"name": "topic", "label": "Essay Topic", "type": "text", "placeholder": "e.g., The impact of AI on education"},
            {"name": "type", "label": "Essay Type", "type": "select", "options": [
                "Argumentative", "Expository", "Narrative", "Descriptive", "Compare & Contrast"
            ], "default": "Argumentative"},
            {"name": "length", "label": "Length", "type": "select", "options": [
                "Short (300-500 words)", "Medium (800-1200 words)", "Long (1500-3000 words)"
            ], "default": "Medium (800-1200 words)"},
            {"name": "thesis", "label": "Thesis / Main Argument (optional)", "type": "textarea", "placeholder": "e.g., AI will enhance rather than replace teachers"},
        ],
        "prompt_builder": lambda fields: (
            f"Write a {fields['type']} essay about: {fields['topic']}\n"
            f"Length: {fields['length']}\n"
            f"Thesis statement: {fields.get('thesis', 'Develop a strong thesis based on the topic')}\n\n"
            f"Include an introduction with thesis, body paragraphs with evidence, "
            f"and a conclusion. Use academic writing style."
        ),
    },

    "story": {
        "name": "Short Story",
        "icon": "📖",
        "description": "Write a creative short story",
        "tool": "write",
        "fields": [
            {"name": "genre", "label": "Genre", "type": "select", "options": [
                "Fantasy", "Sci-Fi", "Mystery", "Romance", "Horror", "Thriller", "Comedy", "Drama"
            ], "default": "Fantasy"},
            {"name": "setting", "label": "Setting", "type": "text", "placeholder": "e.g., A floating city in 2150"},
            {"name": "characters", "label": "Main Characters", "type": "text", "placeholder": "e.g., A young detective and her AI partner"},
            {"name": "idea", "label": "Plot Idea", "type": "textarea", "placeholder": "e.g., A detective discovers that crimes are being predicted by an AI before they happen"},
        ],
        "prompt_builder": lambda fields: (
            f"Write a short story with these details:\n"
            f"Genre: {fields['genre']}\n"
            f"Setting: {fields['setting']}\n"
            f"Main characters: {fields['characters']}\n"
            f"Plot idea: {fields.get('idea', '')}\n\n"
            f"Write an engaging story with a beginning, middle, and end. "
            f"Use vivid descriptions and natural dialogue."
        ),
    },

    "social_media": {
        "name": "Social Media Post",
        "icon": "📱",
        "description": "Create posts for Twitter, LinkedIn, Instagram, etc.",
        "tool": "write",
        "fields": [
            {"name": "platform", "label": "Platform", "type": "select", "options": [
                "Twitter/X", "LinkedIn", "Instagram", "Facebook", "Reddit"
            ], "default": "Twitter/X"},
            {"name": "topic", "label": "Topic", "type": "text", "placeholder": "e.g., Sharing a project I built"},
            {"name": "tone", "label": "Tone", "type": "select", "options": [
                "Professional", "Casual", "Humorous", "Inspirational", "Educational"
            ], "default": "Casual"},
            {"name": "goal", "label": "Goal", "type": "select", "options": [
                "Get engagement", "Share knowledge", "Promote something", "Start a discussion", "Entertain"
            ], "default": "Get engagement"},
        ],
        "prompt_builder": lambda fields: (
            f"Write a {fields['platform']} post about: {fields['topic']}\n"
            f"Tone: {fields['tone']}\n"
            f"Goal: {fields['goal']}\n\n"
            f"Write the post with appropriate hashtags if relevant to the platform. "
            f"Keep it within the platform's character limits."
        ),
    },

    "resume_bullet": {
        "name": "Resume Bullets",
        "icon": "💼",
        "description": "Write powerful resume bullet points",
        "tool": "write",
        "fields": [
            {"name": "job_title", "label": "Job Title", "type": "text", "placeholder": "e.g., Software Developer"},
            {"name": "achievement", "label": "What you did", "type": "textarea", "placeholder": "e.g., Built an automated reporting system"},
            {"name": "metrics", "label": "Results / Numbers", "type": "text", "placeholder": "e.g., Reduced reporting time by 60%, saved 10 hours/week"},
        ],
        "prompt_builder": lambda fields: (
            f"Write 5 strong resume bullet points for a {fields['job_title']} role.\n"
            f"Achievement: {fields['achievement']}\n"
            f"Measurable results: {fields.get('metrics', 'Use realistic placeholder metrics')}\n\n"
            f"Use the STAR method (Situation, Task, Action, Result). "
            f"Start each bullet with a strong action verb. "
            f"Include numbers and metrics where possible."
        ),
    },

    "business_report": {
        "name": "Business Report",
        "icon": "📊",
        "description": "Write a structured business or project report",
        "tool": "write",
        "fields": [
            {"name": "topic", "label": "Report Topic", "type": "text", "placeholder": "e.g., Q3 Sales Performance Review"},
            {"name": "audience", "label": "Audience", "type": "text", "placeholder": "e.g., Senior management, Board of directors"},
            {"name": "data_points", "label": "Key Data / Findings", "type": "textarea", "placeholder": "e.g., Revenue up 15%, customer churn increased 3%"},
            {"name": "recommendations", "label": "Recommendations (if any)", "type": "textarea", "placeholder": "e.g., Invest in customer retention programs"},
        ],
        "prompt_builder": lambda fields: (
            f"Write a professional business report:\n"
            f"Topic: {fields['topic']}\n"
            f"Audience: {fields['audience']}\n"
            f"Key data/findings:\n{fields.get('data_points', '')}\n"
            f"Recommendations:\n{fields.get('recommendations', '')}\n\n"
            f"Use proper report structure: Executive Summary, Introduction, "
            f"Findings, Analysis, Recommendations, Conclusion. "
            f"Use a professional, data-driven tone."
        ),
    },

    "technical_doc": {
        "name": "Technical Documentation",
        "icon": "🔧",
        "description": "Write clear technical documentation",
        "tool": "write",
        "fields": [
            {"name": "subject", "label": "Subject", "type": "text", "placeholder": "e.g., API authentication flow"},
            {"name": "audience_level", "label": "Audience Level", "type": "select", "options": [
                "Beginner", "Intermediate", "Advanced", "Expert"
            ], "default": "Intermediate"},
            {"name": "format", "label": "Format", "type": "select", "options": [
                "Tutorial / How-to", "API Reference", "README", "Architecture Doc", "Troubleshooting Guide"
            ], "default": "Tutorial / How-to"},
            {"name": "details", "label": "Key Details", "type": "textarea", "placeholder": "e.g., Uses OAuth2, requires API key, rate limited to 100 req/min"},
        ],
        "prompt_builder": lambda fields: (
            f"Write technical documentation:\n"
            f"Subject: {fields['subject']}\n"
            f"Audience level: {fields['audience_level']}\n"
            f"Format: {fields['format']}\n"
            f"Key details:\n{fields.get('details', '')}\n\n"
            f"Use clear, precise language. Include code examples where relevant. "
            f"Use proper headings, bullet points, and numbered steps."
        ),
    },
}