"""
SARNA v4.0 — Central Configuration
===================================
Hardwired keywords, subreddit compliance rules, intent phrases,
fallback templates, and system constants. No live API calls for rules.
"""

# =============================================================================
# RSS FEED TARGETS
# Target subreddits for individual RSS fetching
# =============================================================================
TARGET_SUBREDDITS = [
    "shopify", "ecommerce", "smallbusiness", "EntrepreneurIndia",
    "juststart", "DTC", "IndianStartups", "dropship",
    "ShopifyAppDev", "shopifyDev",
]

# =============================================================================
# POST FILTERING & SCORING
MAX_POSTS_PER_RUN = 20

# Relevance scoring weights (out of 100)
SCORE_WEIGHT_INTENT = 40
SCORE_WEIGHT_VALUE = 25
SCORE_WEIGHT_FRESHNESS = 20
SCORE_WEIGHT_BODY_LENGTH = 10
SCORE_WEIGHT_DIVERSITY = 5
MAX_POST_AGE_DAYS = 7
PROCESSED_POSTS_FILE = "processed_posts.json"
PROCESSED_POSTS_MAX = 1000  # Auto-prune older entries
NOTIFICATION_STATE_FILE = "notification_state.json"

# =============================================================================
# INTENT KEYWORDS (60% of captures)
# Posts matching these are explicit problem signals from store owners
# =============================================================================
INTENT_KEYWORDS = [
    "struggling", "help", "not working", "frustrated",
    "can't figure out", "issues with", "stuck with", "failing",
    "sucks", "broken", "how do i", "what am i doing wrong",
    "not converting", "low sales", "traffic drops",
    "no sales", "losing money", "wasting money", "can't sell",
    "conversion rate", "bounce rate", "abandoned cart",
    "ads not working", "seo help", "need advice",
    "what's wrong", "please help", "any suggestions",
    "store review", "critique my", "feedback on",
    "out of stock", "inventory issues", "shipping problems",
    "payment issues", "checkout problems",
]

# =============================================================================
# VALUE KEYWORDS (40% of captures)
# Posts discussing e-commerce topics where expert insight adds value
# =============================================================================
VALUE_KEYWORDS = [
    "increased conversion", "growth strategy", "scaling",
    "how i", "my experience", "case study", "data analysis",
    "optimization", "a]b testing", "analytics",
    "shopify tips", "ecommerce tips", "store setup",
    "product page", "landing page", "email marketing",
    "customer retention", "repeat customers", "brand building",
    "social media strategy", "content marketing",
    "pricing strategy", "competitive analysis",
    "shopify app", "shopify theme", "liquid code",
    "api integration", "webhook", "metafield",
]

# =============================================================================
# DUAL-LAYER SUBREDDIT COMPLIANCE (Hardwired — no live API calls)
#
# Layer 1: Enforced moderation rules (what NOT to do)
# Layer 2: Cultural tone guidelines (how to BLEND IN)
# =============================================================================
SUBREDDIT_COMPLIANCE = {
    "shopify": {
        "layer_1_rules": (
            "No storefront preview loops outside pinned threads. "
            "Absolute ban on promotional outbound linking. "
            "No self-promotion. No soliciting DMs. No AI-generated slop. "
            "Account must be 30+ days old with 20+ comment karma."
        ),
        "layer_2_culture": (
            "Speak like a seasoned technical merchant. Focus on operational "
            "conversion rate details. Reference specific Shopify admin paths. "
            "Practical, no-nonsense tone."
        ),
    },
    "ecommerce": {
        "layer_1_rules": (
            "Immediate removal for dropshipping spam. No links to commercial "
            "platform tiers. Immediate ban WITHOUT warning for any promotion. "
            "No salesy language."
        ),
        "layer_2_culture": (
            "High-level strategic operational alignment. Focus on logistics "
            "and systemic metrics. Data-driven discussion. No hype."
        ),
    },
    "smallbusiness": {
        "layer_1_rules": (
            "Promo only in weekly 'Promote-your-business' thread. "
            "Pain-point mining = ban. Even helpful suggestions with "
            "service mentions get reported."
        ),
        "layer_2_culture": (
            "Practical, down-to-earth. Real business problems, not theory. "
            "Empathetic to small business owner struggles. Casual Q&A vibe."
        ),
    },
    "EntrepreneurIndia": {
        "layer_1_rules": (
            "Strict 9:1 value-to-promotion ratio required by moderation. "
            "No link dumping. Use weekly promo threads if available."
        ),
        "layer_2_culture": (
            "Address localized payment structures (UPI, Razorpay, COD "
            "constraints). Indian market context. Bootstrapping mindset."
        ),
    },
    "juststart": {
        "layer_1_rules": (
            "Text-only, action-oriented. No links without 200+ chars context. "
            "No service promotion. No 'validate my niche' posts."
        ),
        "layer_2_culture": (
            "Founder-focused. Share lessons and tactical breakdowns. "
            "Value case studies and ride-alongs. Hates wantrepreneurs."
        ),
    },
    "DTC": {
        "layer_1_rules": (
            "Founders welcome; no drive-by promos. No astroturfing. "
            "Transparency valued."
        ),
        "layer_2_culture": (
            "DTC mindset. Customer acquisition and brand building. "
            "Behind-the-scenes insights. Founder-to-founder tone."
        ),
    },
    "IndianStartups": {
        "layer_1_rules": (
            "Broadly defines 'self-promotion'; mod discretion is final. "
            "No direct sales, ads, or promotional posts. Use correct flairs."
        ),
        "layer_2_culture": (
            "Indian startup context. Funding, bootstrapping, local market "
            "nuances. Networking-focused discussion."
        ),
    },
    "dropship": {
        "layer_1_rules": (
            "High shadowban risk; community actively reports spam. "
            "Never post store links across multiple subs."
        ),
        "layer_2_culture": (
            "Skeptical audience. Genuine value only; no hype. "
            "Discuss challenges honestly. Anti-spam culture."
        ),
    },
    "ShopifyAppDev": {
        "layer_1_rules": (
            "Developer-focused; technical value only. No marketing pitches. "
            "Code and API discussions."
        ),
        "layer_2_culture": (
            "Code-aware. API patterns, implementation challenges, dev "
            "experience. Technical depth expected. Share code snippets."
        ),
    },
    "shopifyDev": {
        "layer_1_rules": (
            "Developer-focused; development patterns only. "
            "No promotional content."
        ),
        "layer_2_culture": (
            "Technical deep-dives. Implementation details and dev best "
            "practices. Liquid, GraphQL, REST API discussions."
        ),
    },
}

# =============================================================================
# GEMINI CONFIGURATION
# =============================================================================
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_SLEEP_BETWEEN_CALLS = 10  # seconds — keeps us safely under 15 RPM free tier
GEMINI_MAX_RETRIES = 0

# =============================================================================
# GROQ CONFIGURATION (Secondary Fallback)
# =============================================================================
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
# =============================================================================
# GEMINI & GROQ SYSTEM PROMPT TEMPLATE (from PRD — do not modify structure)
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


# =============================================================================
# FALLBACK COMMENT TEMPLATES (human-written, 100% casual)
# Used when Gemini fails after max retries
# =============================================================================
FALLBACK_TEMPLATES = [
    {
        "comment": (
            "yeah i've run into this exact thing before. honestly the biggest "
            "culprit is usually that your product pages are asking people to trust "
            "you with zero social proof: no reviews, no size chart, no clear return "
            "policy. fix those three things and you'll probably see a bump pretty quick. "
            "also worth checking if your meta titles are actually filled in, because "
            "most stores i've looked at have them completely blank, which means google "
            "can't even find you. checking analytics by channel first is usually the best "
            "way to see where the dropoff starts."
        ),
        "dm": (
            "hey, re: my comment on your post, i've been digging into similar "
            "problems for a while. if you want to look into it yourself, the first "
            "thing i would verify is whether your checkout loads under three seconds "
            "on mobile, since that is where most stores leak sales. we also run free "
            "store audits that trace checkout speed and ad waste automatically. "
            "i can run one for your store if you want a second set of eyes."
        ),
    },
    {
        "comment": (
            "one quick thing worth checking today is sorting your products by "
            "inventory and seeing if any of your active ads are pointing to items "
            "that are low stock or completely out. i've seen stores burn serious "
            "money sending paid traffic to pages where people literally can't buy. "
            "it takes about 5 minutes to cross check. tracking conversion rate by "
            "channel is key, since shifting budget to the highest converting channel "
            "is usually the easiest win."
        ),
        "dm": (
            "hey, following up on my comment, this ad spend to inventory mismatch "
            "is more common than you think. checking your ads manager to verify "
            "out of stock product links takes just a few minutes and saves a lot of "
            "budget. we also do free shopify audits that catch exactly this kind of "
            "thing automatically, so feel free to reach out if you want me to run one."
        ),
    },
    {
        "comment": (
            "so this might sound too simple but check if your products actually "
            "have meta titles and descriptions filled in. go to any product in admin, "
            "scroll to the search engine listing preview section at the bottom. if "
            "those are blank, which they are on most stores i've seen, google "
            "basically can't index your stuff. filling those in for your top sellers "
            "takes an afternoon and it is the highest ROI SEO thing you can do."
        ),
        "dm": (
            "hey, re: the SEO stuff i mentioned, most broken link issues come from "
            "old collection urls that were renamed in the admin. checking your "
            "redirects in the online store settings is a great first step. we also "
            "have a tool that scans your entire catalog and flags missing meta fields "
            "automatically. i can run it on your store if you want to double check."
        ),
    },
    {
        "comment": (
            "honestly this is wild but shopify doesn't update a product's url handle "
            "when you rename it in the dashboard. so if you changed a collection name "
            "or product title, the old url slug is still what your instagram bio or "
            "old ad creatives link to. it is worth clicking through all your external "
            "links right now and making sure they actually land where you think. i've "
            "seen bio links silently 404 for months."
        ),
        "dm": (
            "hey, that url handle issue i mentioned bites more stores than you "
            "expect. a quick way to check is using a free chrome extension like "
            "redirect path to audit your social links. we also do free store audits "
            "that catch broken links and inventory mismatches automatically. "
            "i can run one for your store if you want to make sure your links are solid."
        ),
    },
    {
        "comment": (
            "before scaling ad spend, pull up your analytics by channel and compare "
            "conversion rates. in a ton of stores i've looked at, the small amount of "
            "google organic traffic converts much better than paid social. if that "
            "is your case too, investing an afternoon in seo, like meta titles, product "
            "descriptions, and alt text, might get you way more revenue per dollar than "
            "pumping more into instagram."
        ),
        "dm": (
            "hey, re: my comment about channel mismatch, you can compare organic "
            "versus paid social conversion rates directly in your shopify analytics "
            "under reports. we also run free shopify store audits that break down "
            "conversion rate by channel and flag where ad spend is being wasted. "
            "i can run one for your store if you want a breakdown."
        ),
    },
]

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================
EMAIL_RECIPIENT = "pranamyajeet@gmail.com"
EMAIL_SUBJECT_TEMPLATE = "🔍 SARNA — Reddit Opportunities {date} {period}"
GOOGLE_SHEET_URL_TEMPLATE = "https://docs.google.com/spreadsheets/d/{sheet_id}"

# =============================================================================
# GOOGLE SHEETS SCHEMA (6 columns, append-only)
# =============================================================================
SHEET_COLUMNS = ["Subreddit", "Post Title & Link", "AI Suggested Comment",
                 "Subreddit Guidelines", "AI Suggested DM", "Relevance Score"]
SHEET_RANGE = "Sheet1"  # Default sheet tab name
