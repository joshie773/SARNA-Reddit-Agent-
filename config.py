"""
SARNA v4.0 — Central Configuration (Dual-Track AI Automation Pivot)
===================================
Hardwired keywords, subreddit compliance rules, intent phrases,
fallback templates, and system constants for an AI Automation Agency.
"""

# =============================================================================
# RSS FEED TARGETS
# Target subreddits for individual RSS fetching
# =============================================================================
TARGET_SUBREDDITS = [
    "shopify", "ecommerce", "smallbusiness", "EntrepreneurIndia",
    "juststart", "DTC", "IndianStartups", "dropship",
    "ShopifyAppDev", "shopifyDev",
    "Automation", "AI_Agents", "n8n", "zapier", "LocalLLaMA"
]

AI_SUBREDDITS = [
    "Automation", "AI_Agents", "n8n", "zapier", "LocalLLaMA"
]

# =============================================================================
# TIER 1: FOCUSED KEYWORDS (High-Intent, Immediate Problem)
# =============================================================================
INTENT_KEYWORDS_FOCUSED = [
    # E-commerce Metrics
    "conversion rate", "bounce rate", "cart abandonment", "abandoned cart",
    "average order value", "customer lifetime value", "cost per acquisition",
    "not converting", "no sales", "zero sales", "losing sales", "drop in sales",
    "sales dropped", "revenue drop", "ads not working", "roi negative", "bad roas",
    "wasting money", "traffic dropoff", "churn rate", "high cpa", "low roas",
    "repeat customer", "product performance", "inventory turnover", 
    "profit margin", "traffic but no sales", "why am i not getting sales", "getting traffic but",
    "sales have stopped",
    
    # E-commerce Operations & Automation Needs
    "inventory mismatch", "customer support volume", "too many emails", 
    "manual fulfillment", "order processing", "sync inventory", "refund requests", 
    "wasting time on", "repetitive tasks", "manual data entry",
    
    # AI / Automation Specific Needs
    "how to automate", "need a chatbot", "ai agent", "n8n workflow", 
    "zapier integration", "make.com", "webhook", "api integration", 
    "custom gpt", "data extraction", "lead scraping", "crm sync", 
    "auto responder", "too much manual work", "process automation", 
    "workflow error", "automate email"
]

VALUE_KEYWORDS_FOCUSED = [
    "analyzed my metrics", "data shows", "conversion rate by channel",
    "customer cohort", "product performance analysis", "attribution model",
    "funnel analysis", "a/b testing results", "analytics breakdown",
    "revenue by product", "customer acquisition cost", "lifetime value",
    "repeat rate", "segment analysis", "benchmark against",
    "competitive analysis", "traffic source breakdown", "channel performance",
    
    # AI/Automation Context
    "llm workflow", "langchain", "crewai", "autogen", "vector database", 
    "rag pipeline", "python script", "api cost", "token usage"
]

# =============================================================================
# TIER 2: BROADER KEYWORDS
# =============================================================================
INTENT_KEYWORDS_BROADER = [
    "scaling strategy", "growth bottleneck", "optimization",
    "trying to improve", "need to understand", "debugging performance",
    "what's wrong with my store", "how can i improve", "decrease in sales",
    "audit my", "sales struggling", "low sales", "inconsistent sales",
    "need growth", "competitive edge", "market position",
    "pricing strategy", "product mix", "diversify revenue"
]

VALUE_KEYWORDS_BROADER = [
    "growth hacking", "case study", "scaled to", "revenue model",
    "business model", "optimization strategy", "my metrics",
    "store performance", "customer behavior", "purchase pattern",
    "repeat purchase", "brand loyalty", "email marketing metrics",
    "retention strategy", "customer journey", "funnel optimization",
    "marketing mix",
]

# Combine into single list for backwards compatibility
INTENT_KEYWORDS = INTENT_KEYWORDS_FOCUSED + INTENT_KEYWORDS_BROADER
VALUE_KEYWORDS = VALUE_KEYWORDS_FOCUSED + VALUE_KEYWORDS_BROADER

# =============================================================================
# SUBREDDIT WEIGHTING (Multiplier applied to final score)
# =============================================================================
SUBREDDIT_WEIGHT = {
    # AI/Automation Tier 1
    "Automation": 1.5,
    "AI_Agents": 1.5,
    "zapier": 1.5,
    "n8n": 1.4,
    "LocalLLaMA": 1.3,
    
    # E-commerce Tier
    "shopify": 1.4,
    "DTC": 1.3,
    "ecommerce": 1.2,
    "ShopifyAppDev": 1.2,
    "shopifyDev": 1.2,
    
    # Lower value
    "smallbusiness": 0.8,
    "EntrepreneurIndia": 0.7,
    "IndianStartups": 0.7,
    "dropship": 0.6,
    "juststart": 0.5,
}

# =============================================================================
# ANTI-PATTERN FILTERING (Removes low-signal posts)
# =============================================================================
MIN_BODY_LENGTH = 150  # Minimum characters in post body (filters "quick question" posts)

EXCLUDED_PHRASES = [
    "just starting", "brand new", "how do i start", "what's the best",
    "beginner here", "no experience", "first time", "completely new",
    "never done this before", "is dropshipping dead", "start a store",
    "how to start", "new to this", "want to start",
    
    # Noise explicitly added by user
    "best e-commerce site", "cheaper alternative", "scam", "report fake", 
    "how to report", "which platform", "is shopify worth it", "ban", 
    "suspended", "alternative to shopify", "best e-commerce system"
]

# =============================================================================
# SCORING WEIGHTS (Total = 100)
# =============================================================================
SCORE_WEIGHT_INTENT = 50      # Up from 40 — prioritize specific problems
SCORE_WEIGHT_VALUE = 20       # Down from 25 — less emphasis on generic value
SCORE_WEIGHT_FRESHNESS = 15   # Down from 20 — older specific problems still valuable
SCORE_WEIGHT_BODY_LENGTH = 10 # Keep same
SCORE_WEIGHT_DIVERSITY = 5    # Keep same (applied separately in rank_and_select)

MAX_POST_AGE_DAYS = 7
PROCESSED_POSTS_FILE = "processed_posts.json"
PROCESSED_POSTS_MAX = 1000
MAX_POSTS_PER_RUN = 20

# =============================================================================
# DUAL-LAYER SUBREDDIT COMPLIANCE (Hardwired — no live API calls)
# =============================================================================
SUBREDDIT_COMPLIANCE = {
    # -- ECOMMERCE / SHOPIFY SUBREDDITS --
    "shopify": {
        "layer_1_rules": "No storefront preview loops outside pinned threads. Absolute ban on promotional outbound linking. No self-promotion. No soliciting DMs. No AI-generated slop.",
        "layer_2_culture": "Speak like a seasoned technical merchant. Focus on operational conversion rate details. Reference specific Shopify admin paths."
    },
    "ecommerce": {
        "layer_1_rules": "Immediate removal for dropshipping spam. Immediate ban WITHOUT warning for any promotion. No salesy language.",
        "layer_2_culture": "High-level strategic operational alignment. Focus on logistics and systemic metrics. Data-driven discussion. No hype."
    },
    "smallbusiness": {
        "layer_1_rules": "Promo only in weekly 'Promote-your-business' thread. Pain-point mining = ban.",
        "layer_2_culture": "Practical, down-to-earth. Real business problems, not theory. Empathetic to small business owner struggles. Casual Q&A vibe."
    },
    "EntrepreneurIndia": {
        "layer_1_rules": "Strict 9:1 value-to-promotion ratio required by moderation. No link dumping.",
        "layer_2_culture": "Address localized payment structures (UPI, Razorpay, COD constraints). Indian market context. Bootstrapping mindset."
    },
    "juststart": {
        "layer_1_rules": "Text-only, action-oriented. No links without 200+ chars context. No service promotion.",
        "layer_2_culture": "Founder-focused. Share lessons and tactical breakdowns. Value case studies and ride-alongs. Hates wantrepreneurs."
    },
    "DTC": {
        "layer_1_rules": "Founders welcome; no drive-by promos. No astroturfing. Transparency valued.",
        "layer_2_culture": "DTC mindset. Customer acquisition and brand building. Behind-the-scenes insights. Founder-to-founder tone."
    },
    "IndianStartups": {
        "layer_1_rules": "Broadly defines 'self-promotion'; mod discretion is final. No direct sales, ads, or promotional posts.",
        "layer_2_culture": "Indian startup context. Funding, bootstrapping, local market nuances. Networking-focused discussion."
    },
    "dropship": {
        "layer_1_rules": "High shadowban risk; community actively reports spam. Never post store links across multiple subs.",
        "layer_2_culture": "Skeptical audience. Genuine value only; no hype. Discuss challenges honestly. Anti-spam culture."
    },
    "ShopifyAppDev": {
        "layer_1_rules": "Developer-focused; technical value only. No marketing pitches. Code and API discussions.",
        "layer_2_culture": "Code-aware. API patterns, implementation challenges, dev experience. Technical depth expected. Share code snippets."
    },
    "shopifyDev": {
        "layer_1_rules": "Developer-focused; development patterns only. No promotional content.",
        "layer_2_culture": "Technical deep-dives. Implementation details and dev best practices. Liquid, GraphQL, REST API discussions."
    },
    
    # -- AI / AUTOMATION SUBREDDITS --
    "Automation": {
        "layer_1_rules": "No spammy software promotion. Technical discussion and real-world workflow help only.",
        "layer_2_culture": "Process-oriented. Value efficient architectures and identifying where human bottlenecks exist. Speak like an operations expert."
    },
    "AI_Agents": {
        "layer_1_rules": "No low-effort wrapper app promos. Focus on agentic workflows and implementation architecture.",
        "layer_2_culture": "Highly technical. Discuss prompt engineering, tool use, LLM capabilities, and orchestration (LangChain, CrewAI, AutoGen)."
    },
    "zapier": {
        "layer_1_rules": "No self-promotion of competing tools. Help users debug Zaps.",
        "layer_2_culture": "Action-oriented. Talk about triggers, actions, webhooks, and API limits. Be incredibly practical."
    },
    "n8n": {
        "layer_1_rules": "No spam. Focus on node-based workflow debugging and self-hosted implementations.",
        "layer_2_culture": "Developer/tinker mindset. Appreciate complex JSON parsing, HTTP nodes, and self-hosted open-source ethos."
    },
    "LocalLLaMA": {
        "layer_1_rules": "No commercial spam. Strictly open-source, local models, and technical AI discussion.",
        "layer_2_culture": "Incredibly technical and anti-commercial. Hate closed APIs. Focus on quantization, model fine-tuning, and hardware constraints."
    }
}

# =============================================================================
# GEMINI & GROQ CONFIGURATION
# =============================================================================
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_SLEEP_BETWEEN_CALLS = 10
GEMINI_MAX_RETRIES = 0

GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_API_BASE = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MAX_RETRIES = 1

# Words that trigger automatic regeneration or fallback
BANNED_WORDS = [
    "we recommend", "leverage", "strategic", "dm me", "synergize",
    "optimize", "check out", "our tool", "our service", "our product",
    "sahajta", "game-changing", "revolutionary", "best solution",
    "reach out", "don't hesitate", "cutting-edge", "industry-leading",
    "sophisticated", "implementation", "facilitate", "utilize",
    "regarding", "concerning", "endeavor", "maximize roi",
    "strategic frameworks", "solutions",
]

# =============================================================================
# ECOMMERCE: SYSTEM PROMPT & FALLBACKS
# =============================================================================
SYSTEM_PROMPT_TEMPLATE = """You are a highly experienced, real-world e-commerce founder hanging out on Reddit (r/{subreddit_name}). You aren't an AI, a marketer, or a corporate bot. You're just a person who has been in the trenches and genuinely wants to help someone out.

You need to draft a public comment and a private DM in response to a post.

Strict Compliance Layers:
Layer 1 (Subreddit Rules): {layer_1_rules}
Layer 2 (Subreddit Culture): {layer_2_culture}

How to write (Raw Reddit Voice):
- Sound completely authentic, warm, and casual. Talk like you're speaking to a peer. 
- Give immediate, tactical, actionable advice based on your "experience". 
- Do NOT use formal structure or overly polished language. Use lowercase, contractions, and natural pacing. 
- NEVER use em-dashes (—) or mid-sentence dashes (-).
- At the end of the DM, add a gentle, soft statement offering a free audit (e.g., "i can run a free audit on your store if you want a second set of eyes."). Do NOT ask a question.
- CRITICAL BANNED WORDS: "we recommend", "leverage", "strategic", "DM me", "synergize", "optimize". If you sound corporate, you fail.

Output a strictly formatted JSON object containing exactly two keys: "comment" (Max 150 words) and "dm" (Max 100 words).
Output ONLY the raw JSON object. No markdown fences, no preamble, no explanation."""

FALLBACK_TEMPLATES = [
    {
        "comment": "yeah i've run into this exact thing before. honestly the biggest culprit is usually that your product pages are asking people to trust you with zero social proof. fix that and you'll probably see a bump pretty quick.",
        "dm": "hey, re: my comment on your post, i've been digging into similar problems for a while. if you want to look into it yourself, verify your checkout loads fast on mobile. i can run a free audit on your store if you want a second set of eyes."
    }
]

# =============================================================================
# AI/AUTOMATION: SYSTEM PROMPT & FALLBACKS
# =============================================================================
SYSTEM_PROMPT_TEMPLATE_AI = """You are a highly experienced, real-world AI automation and systems architect hanging out on Reddit (r/{subreddit_name}). You aren't a generic marketer, a hype-bro, or a corporate bot. You're just a technical person who builds real automations (n8n, Zapier, LLM workflows) and genuinely wants to help someone out.

You need to draft a public comment and a private DM in response to a post.

Strict Compliance Layers:
Layer 1 (Subreddit Rules): {layer_1_rules}
Layer 2 (Subreddit Culture): {layer_2_culture}

How to write (Raw Reddit Voice):
- Sound completely authentic, technical, and casual. Talk like you're speaking to a fellow builder or operator.
- Give immediate, tactical, actionable advice based on your "experience" building these workflows.
- Do NOT use formal structure or overly polished language. Use lowercase, contractions, and natural pacing.
- NEVER use em-dashes (—) or mid-sentence dashes (-).
- At the end of the DM, add a gentle, soft statement offering a free workflow architecture review (e.g., "i can map out a free workflow architecture for this if you want a second set of eyes."). Do NOT ask a question.
- CRITICAL BANNED WORDS: "we recommend", "leverage", "strategic", "DM me", "synergize", "optimize", "game-changing". If you sound corporate or like an "AI guru", you fail.

Output a strictly formatted JSON object containing exactly two keys: "comment" (Max 150 words) and "dm" (Max 100 words).
Output ONLY the raw JSON object. No markdown fences, no preamble, no explanation."""

FALLBACK_TEMPLATES_AI = [
    {
        "comment": "yeah hitting api limits or getting timeout errors on these workflows is super common. usually the easiest fix is adding a small delay node or switching to a webhook instead of polling. saves a ton of tasks/compute too.",
        "dm": "hey, re: my comment on your workflow post, i build out these kinds of automations a lot. if you are still stuck on it, usually breaking the flow into two separate scenarios solves the timeout issues. i can map out a free workflow architecture for this if you want a second set of eyes."
    }
]

# =============================================================================
# EMAIL CONFIGURATION & GOOGLE SHEETS
# =============================================================================
EMAIL_RECIPIENT = "pranamyajeet@gmail.com"
EMAIL_SUBJECT_TEMPLATE = "🔍 SARNA — Reddit Opportunities {date} {period}"
GOOGLE_SHEET_URL_TEMPLATE = "https://docs.google.com/spreadsheets/d/{sheet_id}"
NOTIFICATION_STATE_FILE = "notification_state.json"

SHEET_COLUMNS = ["Subreddit", "Post Title & Link", "AI Suggested Comment",
                 "Subreddit Guidelines", "AI Suggested DM", "Relevance Score"]
SHEET_RANGE = "Sheet1"
