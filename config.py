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
# GEMINI SYSTEM PROMPT TEMPLATE (from PRD — do not modify structure)
# =============================================================================
SYSTEM_PROMPT_TEMPLATE = """You are an elite AI networking agent for Sahajta AI. Your goal is to draft a helpful public comment and a private DM response for a post in r/{subreddit_name}.
You must strictly adhere to the following two compliance layers:

Layer 1: CURRENT LIVE SUBREDDIT RULES (Enforced Banned Actions):
{layer_1_rules}

Layer 2: COMMUNITY CULTURE & TONE GUIDELINES (How to blend in):
{layer_2_culture}

Instructions:
1. Public Comment (The Give): Use the principle of Reciprocity. Give them an immediate, tactical solution to their problem for free. Validate their struggle ("yeah i've seen this happen"), tell them exactly what to fix, but intentionally leave out the *how* to create a Curiosity Gap. End with an open question.
2. Private DM (The Hook): Use the principle of Authority & Low Friction. Reference your comment so they recognize you. Soft-pitch a free, zero-friction offer (e.g., "we run free store audits that catch exactly this. no strings.").
3. Safety First: Cross-reference your draft against Layer 1. If Layer 1 says "No self-promotion," your public comment cannot mention your company at all.
4. Tone: Adopt the tone specified in Layer 2. TONE IS EVERYTHING. Sound like a knowledgeable, helpful Redditor. Use contractions. Use first-person ("i've seen", "imo"). Use lowercase.
5. BANNED WORDS: "we recommend", "leverage", "strategic", "DM me", "synergize", "optimize". If your output reads polished or corporate, you fail.

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
            "can't even find you. where is most of your traffic coming from right now?"
        ),
        "dm": (
            "hey, re: my comment on your post... i've been digging into similar "
            "problems for a while. we actually run free store audits for shopify "
            "brands that covers exactly the stuff i mentioned (seo gaps, ad waste, "
            "conversion blockers). no strings. want me to run one for your store?"
        ),
    },
    {
        "comment": (
            "one quick thing worth checking today: go to your products, sort by "
            "inventory, and see if any of your active ads are pointing to items "
            "that are low stock or completely out. i've seen stores burn serious "
            "money sending paid traffic to pages where people literally can't buy. "
            "takes like 5 minutes to cross-check. also, are you tracking conversion "
            "rate by channel? sometimes one channel converts way better and you "
            "just need to shift budget."
        ),
        "dm": (
            "hey, following up on my comment, this ad-spend-to-inventory mismatch "
            "is more common than you'd think. we do free shopify audits that catch "
            "exactly this kind of thing automatically. happy to run one for you "
            "if you're interested, zero cost."
        ),
    },
    {
        "comment": (
            "so this might sound too simple but check if your products actually "
            "have meta titles and descriptions filled in. go to any product in admin, "
            "scroll to the 'search engine listing preview' section at the bottom. if "
            "those are blank (which they are on like 90% of stores i've seen), google "
            "basically can't index your stuff. filling those in for your top sellers "
            "takes an afternoon and it's honestly the highest-roi seo thing you can do."
        ),
        "dm": (
            "hey, re: the seo stuff i mentioned, we actually have a tool that "
            "scans your entire shopify catalog and flags every missing meta field, "
            "broken url handle, and seo gap automatically. free audit, no catch. "
            "want me to run it on your store?"
        ),
    },
    {
        "comment": (
            "honestly this is wild but shopify doesn't update a product's url handle "
            "when you rename it in the dashboard. so if you changed a collection name "
            "or product title, the old url slug is still what your instagram bio or "
            "old ad creatives link to. worth clicking through all your external links "
            "right now and making sure they actually land where you think. i've seen "
            "bio links silently 404 for months."
        ),
        "dm": (
            "hey, that url handle issue i mentioned bites more stores than you'd "
            "expect. we do free store audits that catch broken links, seo gaps, "
            "and inventory mismatches automatically. want me to run one for your "
            "store? takes about a day, zero cost."
        ),
    },
    {
        "comment": (
            "before scaling ad spend, pull up your analytics by channel and compare "
            "conversion rates. in a ton of stores i've looked at, the small amount of "
            "google organic traffic converts like 4-6x better than paid social. if "
            "that's your case too, investing an afternoon in seo (meta titles, product "
            "descriptions, alt text) might get you way more revenue per dollar than "
            "pumping more into instagram. worth checking at least."
        ),
        "dm": (
            "hey, re: my comment about channel mismatch... we run free shopify "
            "store audits that break down conversion rate by channel and flag "
            "exactly where money is being wasted vs. where it's converting. "
            "happy to do one for your store if you want."
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
