"""Business Categories — 50 online businesses a solo founder can run with AI.

Each entry: capability -> native handler coverage, revenue method (Zoho),
worldwide/India TAM, autonomy. Powering the Business Factory.

Source tiers at cutoff: Statista / Grand View / IMARC triangulated TAM ranges.
TAM = total addressable, not SAM. Use for ranking, not audited P&L.
Money is INR-native (Zoho Payments/Books). USD shown for worldwide ranking.
"""
from __future__ import annotations

CATEGORIES: dict[str, dict] = {
    # A — Knowledge & Media (GREEN 90-98% autonomous)
    "paid_research_reports": {"id": "paid_research_reports", "label": "Paid Research Reports", "tier": "A", "group": "knowledge", "autonomy_pct": 98, "worldwide_usd_b": 50, "india_usd_b": 1.35, "capabilities": ["email", "invoicing", "customer_relationship"], "handlers": ["GMAIL", "ZOHO", "TAVILY"], "revenue_method": "one_time", "price_inr": 999, "margin_pct": 90, "description": "Tavily research -> LLM report -> Zoho invoice -> Gmail delivery"},
    "paid_newsletter": {"id": "paid_newsletter", "label": "Paid Newsletter", "tier": "A", "group": "knowledge", "autonomy_pct": 95, "worldwide_usd_b": 10, "india_usd_b": 0.22, "capabilities": ["email", "invoicing"], "handlers": ["GMAIL", "ZOHO", "TAVILY"], "revenue_method": "mandate", "price_inr": 499, "margin_pct": 85, "description": "Daily brief via Tavily Deep Research + Gmail batch"},
    "prompt_template_packs": {"id": "prompt_template_packs", "label": "Prompt/Template Packs", "tier": "A", "group": "knowledge", "autonomy_pct": 98, "worldwide_usd_b": 1.5, "india_usd_b": 0.10, "capabilities": ["email", "invoicing"], "handlers": ["GMAIL", "ZOHO"], "revenue_method": "one_time", "price_inr": 399, "margin_pct": 95, "description": "Notion/Github deliverable packs"},
    "notion_template_store": {"id": "notion_template_store", "label": "Notion Template Store", "tier": "A", "group": "knowledge", "autonomy_pct": 96, "worldwide_usd_b": 0.4, "india_usd_b": 0.02, "capabilities": ["email", "invoicing"], "handlers": ["GMAIL", "ZOHO", "NOTION"], "revenue_method": "one_time", "price_inr": 499, "margin_pct": 92, "description": "Systems, CRMs, OKRs as Notion templates"},
    "seo_affiliate_site": {"id": "seo_affiliate_site", "label": "SEO Affiliate Content Site", "tier": "A", "group": "knowledge", "autonomy_pct": 92, "worldwide_usd_b": 22, "india_usd_b": 1.05, "capabilities": ["email", "invoicing"], "handlers": ["TAVILY", "GITHUB", "GMAIL", "ZOHO"], "revenue_method": "affiliate", "price_inr": 0, "margin_pct": 70, "description": "Tavily keywords -> LLM article -> Github deploy -> affiliate + Zoho accounting"},
    "online_course_async": {"id": "online_course_async", "label": "Online Course (async)", "tier": "A", "group": "knowledge", "autonomy_pct": 94, "worldwide_usd_b": 225, "india_usd_b": 9.0, "capabilities": ["email", "invoicing", "customer_relationship"], "handlers": ["GMAIL", "ZOHO", "NOTION"], "revenue_method": "one_time", "price_inr": 1999, "margin_pct": 88, "description": "Video + Notion docs, async delivery"},
    "cohort_course": {"id": "cohort_course", "label": "Cohort Course (automated)", "tier": "A", "group": "knowledge", "autonomy_pct": 88, "worldwide_usd_b": 5, "india_usd_b": 0.50, "capabilities": ["email", "invoicing"], "handlers": ["GMAIL", "ZOHO", "NOTION"], "revenue_method": "one_time", "price_inr": 4999, "margin_pct": 80, "description": "Drip via Gmail + Notion"},
    "ebook_playbook": {"id": "ebook_playbook", "label": "E-book / Playbook", "tier": "A", "group": "knowledge", "autonomy_pct": 98, "worldwide_usd_b": 16, "india_usd_b": 0.45, "capabilities": ["email", "invoicing"], "handlers": ["GMAIL", "ZOHO", "GITHUB"], "revenue_method": "one_time", "price_inr": 399, "margin_pct": 95, "description": "LLM generate + Github PDF delivery"},
    "industry_database": {"id": "industry_database", "label": "Industry Database", "tier": "A", "group": "knowledge", "autonomy_pct": 90, "worldwide_usd_b": 27, "india_usd_b": 0.70, "capabilities": ["email", "invoicing"], "handlers": ["TAVILY", "PARALLEL", "ZOHO"], "revenue_method": "mandate", "price_inr": 1999, "margin_pct": 85, "description": "Scraped + enriched via Tavily/Parallel"},
    "job_board_niche": {"id": "job_board_niche", "label": "Job Board (niche)", "tier": "A", "group": "knowledge", "autonomy_pct": 78, "worldwide_usd_b": 55, "india_usd_b": 2.25, "capabilities": ["email", "invoicing", "customer_relationship"], "handlers": ["PARALLEL", "GMAIL", "ZOHO"], "revenue_method": "mandate", "price_inr": 1999, "margin_pct": 75, "description": "Scrape + Gmail alerts"},

    # B — Software & Tools
    "micro_saas": {"id": "micro_saas", "label": "Micro-SaaS (single API)", "tier": "B", "group": "software", "autonomy_pct": 90, "worldwide_usd_b": 35, "india_usd_b": 1.75, "capabilities": ["email", "invoicing", "payment_processing", "code_review"], "handlers": ["GITHUB", "ZOHO", "GMAIL"], "revenue_method": "mandate", "price_inr": 4999, "margin_pct": 80, "description": "FX API, PDF parser, Invoice reminder bot - dogfoods zoho handler"},
    "no_code_automation": {"id": "no_code_automation", "label": "No-Code Automation Tools", "tier": "B", "group": "software", "autonomy_pct": 88, "worldwide_usd_b": 30, "india_usd_b": 0.90, "capabilities": ["email", "invoicing"], "handlers": ["GITHUB", "ZOHO"], "revenue_method": "mandate", "price_inr": 1999, "margin_pct": 85, "description": "Zap-like for Zoho<>Gmail"},
    "ai_chatbot_widget": {"id": "ai_chatbot_widget", "label": "AI Chatbot/Support Widget", "tier": "B", "group": "software", "autonomy_pct": 92, "worldwide_usd_b": 12, "india_usd_b": 0.60, "capabilities": ["email", "invoicing", "customer_relationship"], "handlers": ["GMAIL", "ZOHO", "NOTION"], "revenue_method": "mandate", "price_inr": 1999, "margin_pct": 82, "description": "Site widget via Gmail + Notion KB (RAPTOR)"},
    "browser_extension": {"id": "browser_extension", "label": "Browser Extension", "tier": "B", "group": "software", "autonomy_pct": 85, "worldwide_usd_b": 2.5, "india_usd_b": 0.10, "capabilities": ["email", "invoicing", "code_review"], "handlers": ["GITHUB", "ZOHO"], "revenue_method": "one_time", "price_inr": 499, "margin_pct": 90, "description": "Productivity overlay"},
    "notion_github_integrations": {"id": "notion_github_integrations", "label": "Notion/GitHub Integrations", "tier": "B", "group": "software", "autonomy_pct": 90, "worldwide_usd_b": 4, "india_usd_b": 0.18, "capabilities": ["email", "invoicing", "code_review"], "handlers": ["GITHUB", "NOTION", "ZOHO"], "revenue_method": "mandate", "price_inr": 999, "margin_pct": 88, "description": "Sync, backup, reports"},
    "ai_writing_assistant": {"id": "ai_writing_assistant", "label": "AI Writing Assistant (niche)", "tier": "B", "group": "software", "autonomy_pct": 88, "worldwide_usd_b": 3, "india_usd_b": 0.25, "capabilities": ["email", "invoicing"], "handlers": ["GITHUB", "ZOHO"], "revenue_method": "mandate", "price_inr": 499, "margin_pct": 85, "description": "Real estate listings, ad copy niche"},
    "ai_voice_audio": {"id": "ai_voice_audio", "label": "AI Voice/Audio Tools", "tier": "B", "group": "software", "autonomy_pct": 72, "worldwide_usd_b": 5, "india_usd_b": 0.35, "capabilities": ["email", "invoicing"], "handlers": ["GITHUB", "ZOHO"], "revenue_method": "mandate", "price_inr": 999, "margin_pct": 70, "description": "Transcribe, dub (wrap external API)"},
    "data_enrichment_api": {"id": "data_enrichment_api", "label": "Data Enrichment API", "tier": "B", "group": "software", "autonomy_pct": 90, "worldwide_usd_b": 10, "india_usd_b": 0.50, "capabilities": ["email", "invoicing"], "handlers": ["TAVILY", "FRANKFURTER", "ZOHO"], "revenue_method": "mandate", "price_inr": 1999, "margin_pct": 85, "description": "Tavily + Frankfurter -> leads API"},
    "resume_proposal_generator": {"id": "resume_proposal_generator", "label": "Resume/Proposal Generator", "tier": "B", "group": "software", "autonomy_pct": 92, "worldwide_usd_b": 1.5, "india_usd_b": 0.20, "capabilities": ["email", "invoicing"], "handlers": ["GITHUB", "ZOHO"], "revenue_method": "one_time", "price_inr": 399, "margin_pct": 90, "description": "LLM + Notion template"},
    "website_builder_ai": {"id": "website_builder_ai", "label": "Website Builder (AI)", "tier": "B", "group": "software", "autonomy_pct": 90, "worldwide_usd_b": 13, "india_usd_b": 0.90, "capabilities": ["email", "invoicing", "code_review"], "handlers": ["GITHUB", "ZOHO"], "revenue_method": "one_time", "price_inr": 999, "margin_pct": 85, "description": "SMARTDECIGEN_BUILD -> Github deploy"},

    # C — Productized Services (Small team, Large impact)
    "seo_service": {"id": "seo_service", "label": "SEO Service (productized)", "tier": "C", "group": "services", "autonomy_pct": 88, "worldwide_usd_b": 100, "india_usd_b": 4.0, "capabilities": ["email", "invoicing"], "handlers": ["TAVILY", "GMAIL", "ZOHO"], "revenue_method": "invoice", "price_inr": 9999, "margin_pct": 65, "description": "Tavily audit -> Gmail report -> Zoho invoice"},
    "cold_outreach_agency": {"id": "cold_outreach_agency", "label": "Cold Outreach Agency", "tier": "C", "group": "services", "autonomy_pct": 80, "worldwide_usd_b": 7, "india_usd_b": 0.45, "capabilities": ["email", "invoicing"], "handlers": ["GMAIL", "TAVILY", "ZOHO"], "revenue_method": "invoice", "price_inr": 15000, "margin_pct": 55, "description": "Gmail search -> enrich -> Gmail send (L3 approval)"},
    "bookkeeping_automation": {"id": "bookkeeping_automation", "label": "Bookkeeping Automation", "tier": "C", "group": "services", "autonomy_pct": 92, "worldwide_usd_b": 17, "india_usd_b": 1.75, "capabilities": ["email", "invoicing", "customer_relationship"], "handlers": ["ZOHO", "GMAIL"], "revenue_method": "mandate", "price_inr": 4999, "margin_pct": 75, "description": "Zoho Books: list invoices -> categorize -> Gmail reminder"},
    "invoice_chasing_service": {"id": "invoice_chasing_service", "label": "Invoice Chasing Service", "tier": "C", "group": "services", "autonomy_pct": 90, "worldwide_usd_b": 4, "india_usd_b": 0.25, "capabilities": ["email", "invoicing"], "handlers": ["ZOHO", "GMAIL"], "revenue_method": "invoice", "price_inr": 0, "margin_pct": 80, "description": "run_cash_loop as product (% of collected)"},
    "recruitment_sourcing": {"id": "recruitment_sourcing", "label": "Recruitment Sourcing", "tier": "C", "group": "services", "autonomy_pct": 82, "worldwide_usd_b": 35, "india_usd_b": 2.75, "capabilities": ["email", "invoicing"], "handlers": ["TAVILY", "GMAIL", "ZOHO"], "revenue_method": "invoice", "price_inr": 20000, "margin_pct": 60, "description": "Tavily + Gmail outreach for hiring"},
    "ad_campaign_management": {"id": "ad_campaign_management", "label": "Ad Campaign Management", "tier": "C", "group": "services", "autonomy_pct": 65, "worldwide_usd_b": 120, "india_usd_b": 11.0, "capabilities": ["email", "invoicing"], "handlers": ["GMAIL", "ZOHO"], "revenue_method": "invoice", "price_inr": 15000, "margin_pct": 50, "description": "Brief -> LLM copy -> Gmail approve (Ads API = Composio)"},
    "social_media_mgmt": {"id": "social_media_mgmt", "label": "Social Media Management (AI)", "tier": "C", "group": "services", "autonomy_pct": 60, "worldwide_usd_b": 22, "india_usd_b": 1.35, "capabilities": ["email", "invoicing"], "handlers": ["GMAIL", "ZOHO"], "revenue_method": "mandate", "price_inr": 4999, "margin_pct": 55, "description": "Calendar -> Gmail/Slack draft (posting = Composio)"},
    "customer_support_outsourcing": {"id": "customer_support_outsourcing", "label": "Customer Support Outsourcing", "tier": "C", "group": "services", "autonomy_pct": 88, "worldwide_usd_b": 110, "india_usd_b": 13.5, "capabilities": ["email", "invoicing"], "handlers": ["GMAIL", "ZOHO"], "revenue_method": "invoice", "price_inr": 999, "margin_pct": 60, "description": "Gmail search -> draft reply (L3) -> Zoho invoice"},
    "market_research_ondemand": {"id": "market_research_ondemand", "label": "Market Research on Demand", "tier": "C", "group": "services", "autonomy_pct": 92, "worldwide_usd_b": 85, "india_usd_b": 2.75, "capabilities": ["email", "invoicing"], "handlers": ["TAVILY", "NOTION", "ZOHO"], "revenue_method": "one_time", "price_inr": 4999, "margin_pct": 80, "description": "Tavily Deep Research -> Notion deck -> Zoho invoice"},
    "sales_crm_setup": {"id": "sales_crm_setup", "label": "Sales CRM Setup (Zoho)", "tier": "C", "group": "services", "autonomy_pct": 90, "worldwide_usd_b": 65, "india_usd_b": 2.0, "capabilities": ["email", "invoicing", "customer_relationship"], "handlers": ["ZOHO", "NOTION"], "revenue_method": "one_time", "price_inr": 9999, "margin_pct": 75, "description": "Configure Zoho Books/CRM for client"},

    # D — Commerce & Marketplace
    "digital_product_marketplace": {"id": "digital_product_marketplace", "label": "Digital Product Marketplace", "tier": "D", "group": "commerce", "autonomy_pct": 85, "worldwide_usd_b": 17, "india_usd_b": 0.50, "capabilities": ["email", "invoicing", "payment_processing"], "handlers": ["GITHUB", "ZOHO"], "revenue_method": "one_time", "price_inr": 499, "margin_pct": 80, "description": "Gumroad-style via Github + Zoho checkout"},
    "print_on_demand": {"id": "print_on_demand", "label": "Print-on-Demand", "tier": "D", "group": "commerce", "autonomy_pct": 55, "worldwide_usd_b": 10, "india_usd_b": 0.45, "capabilities": ["email", "invoicing"], "handlers": ["ZOHO"], "revenue_method": "one_time", "price_inr": 799, "margin_pct": 40, "description": "Design LLM -> Composio:printful -> Zoho invoice"},
    "dropshipping": {"id": "dropshipping", "label": "Dropshipping (curated)", "tier": "D", "group": "commerce", "autonomy_pct": 55, "worldwide_usd_b": 275, "india_usd_b": 9.0, "capabilities": ["email", "invoicing"], "handlers": ["TAVILY", "ZOHO"], "revenue_method": "one_time", "price_inr": 999, "margin_pct": 35, "description": "Tavily research -> Shopify (Composio) - manual today"},
    "affiliate_store_niche": {"id": "affiliate_store_niche", "label": "Affiliate Store (niche)", "tier": "D", "group": "commerce", "autonomy_pct": 88, "worldwide_usd_b": 22, "india_usd_b": 1.05, "capabilities": ["email", "invoicing"], "handlers": ["TAVILY", "GITHUB", "ZOHO"], "revenue_method": "affiliate", "price_inr": 0, "margin_pct": 50, "description": "SEO site + affiliate links"},
    "stock_photo_video_ai": {"id": "stock_photo_video_ai", "label": "Stock Photo/Video AI", "tier": "D", "group": "commerce", "autonomy_pct": 80, "worldwide_usd_b": 6, "india_usd_b": 0.25, "capabilities": ["email", "invoicing"], "handlers": ["GITHUB", "ZOHO"], "revenue_method": "one_time", "price_inr": 499, "margin_pct": 85, "description": "Generate -> sell via Github + Zoho"},
    "domain_flipping": {"id": "domain_flipping", "label": "Domain Flipping", "tier": "D", "group": "commerce", "autonomy_pct": 82, "worldwide_usd_b": 1.5, "india_usd_b": 0.07, "capabilities": ["email", "invoicing"], "handlers": ["TAVILY", "GMAIL", "ZOHO"], "revenue_method": "one_time", "price_inr": 1999, "margin_pct": 70, "description": "Tavily trends -> Gmail outreach -> Zoho invoice"},
    "app_store_micro": {"id": "app_store_micro", "label": "App Store (micro-apps)", "tier": "D", "group": "commerce", "autonomy_pct": 85, "worldwide_usd_b": 12, "india_usd_b": 0.60, "capabilities": ["email", "invoicing", "code_review"], "handlers": ["GITHUB", "ZOHO"], "revenue_method": "one_time", "price_inr": 499, "margin_pct": 80, "description": "PWA per niche, Github deploy"},
    "b2b_lead_marketplace": {"id": "b2b_lead_marketplace", "label": "B2B Lead Marketplace", "tier": "D", "group": "commerce", "autonomy_pct": 88, "worldwide_usd_b": 6.5, "india_usd_b": 0.35, "capabilities": ["email", "invoicing"], "handlers": ["PARALLEL", "ZOHO"], "revenue_method": "mandate", "price_inr": 1999, "margin_pct": 75, "description": "Parallel extract -> sell CSV via Zoho"},

    # E — Creator & Community
    "paid_community": {"id": "paid_community", "label": "Paid Community", "tier": "E", "group": "community", "autonomy_pct": 82, "worldwide_usd_b": 6.5, "india_usd_b": 0.35, "capabilities": ["email", "invoicing"], "handlers": ["GMAIL", "NOTION", "SLACK", "ZOHO"], "revenue_method": "mandate", "price_inr": 999, "margin_pct": 85, "description": "Skool/Discord ops via Gmail+Notion+Slack"},
    "coaching_async": {"id": "coaching_async", "label": "Coaching (async, productized)", "tier": "E", "group": "community", "autonomy_pct": 90, "worldwide_usd_b": 22, "india_usd_b": 1.25, "capabilities": ["email", "invoicing"], "handlers": ["GMAIL", "ZOHO"], "revenue_method": "mandate", "price_inr": 1999, "margin_pct": 85, "description": "GoalThread engine as product (engine.py)"},
    "cohort_community_course": {"id": "cohort_community_course", "label": "Cohort Community + Course", "tier": "E", "group": "community", "autonomy_pct": 80, "worldwide_usd_b": 8, "india_usd_b": 0.60, "capabilities": ["email", "invoicing"], "handlers": ["NOTION", "GMAIL", "ZOHO"], "revenue_method": "one_time", "price_inr": 4999, "margin_pct": 78, "description": "Notion + Gmail drip cohort"},
    "youtube_automation": {"id": "youtube_automation", "label": "YouTube Automation (faceless)", "tier": "E", "group": "community", "autonomy_pct": 55, "worldwide_usd_b": 37, "india_usd_b": 1.75, "capabilities": ["email", "invoicing"], "handlers": ["TAVILY", "ZOHO"], "revenue_method": "affiliate", "price_inr": 0, "margin_pct": 60, "description": "Script LLM -> Tavily research -> editor manual, upload via Composio"},
    "podcast_network_ai": {"id": "podcast_network_ai", "label": "Podcast Network (AI)", "tier": "E", "group": "community", "autonomy_pct": 75, "worldwide_usd_b": 4.5, "india_usd_b": 0.18, "capabilities": ["email", "invoicing"], "handlers": ["GMAIL", "NOTION", "ZOHO"], "revenue_method": "invoice", "price_inr": 9999, "margin_pct": 65, "description": "Show notes -> Notion -> Gmail, sponsor invoice"},
    "membership_site": {"id": "membership_site", "label": "Membership Site", "tier": "E", "group": "community", "autonomy_pct": 88, "worldwide_usd_b": 12, "india_usd_b": 0.50, "capabilities": ["email", "invoicing", "payment_processing"], "handlers": ["GITHUB", "ZOHO"], "revenue_method": "mandate", "price_inr": 999, "margin_pct": 85, "description": "Github + Zoho gate (deduct_tokens)"},

    # F — Data & Finance (Frankfurter = always_works)
    "fx_finance_api": {"id": "fx_finance_api", "label": "FX/Finance API", "tier": "F", "group": "finance", "autonomy_pct": 98, "worldwide_usd_b": 4, "india_usd_b": 0.25, "capabilities": ["email", "invoicing"], "handlers": ["FRANKFURTER", "ZOHO"], "revenue_method": "mandate", "price_inr": 499, "margin_pct": 90, "description": "Frankfurter (free FX) -> Zoho billing, 0 config"},
    "credit_loan_leadgen": {"id": "credit_loan_leadgen", "label": "Credit/Loan Lead Gen", "tier": "F", "group": "finance", "autonomy_pct": 85, "worldwide_usd_b": 17, "india_usd_b": 2.50, "capabilities": ["email", "invoicing"], "handlers": ["TAVILY", "GMAIL", "ZOHO"], "revenue_method": "invoice", "price_inr": 500, "margin_pct": 70, "description": "Tavily + Gmail qualify -> per-lead Zoho invoice, India fintech boom"},
    "expense_audit_tool": {"id": "expense_audit_tool", "label": "Expense Audit Tool", "tier": "F", "group": "finance", "autonomy_pct": 88, "worldwide_usd_b": 6.5, "india_usd_b": 0.35, "capabilities": ["email", "invoicing"], "handlers": ["ZOHO", "GMAIL"], "revenue_method": "mandate", "price_inr": 1999, "margin_pct": 80, "description": "Zoho invoices -> LLM flag waste -> Gmail report"},
    "tax_filing_assistant": {"id": "tax_filing_assistant", "label": "Tax Filing Assistant (India)", "tier": "F", "group": "finance", "autonomy_pct": 75, "worldwide_usd_b": 1.5, "india_usd_b": 0.50, "capabilities": ["email", "invoicing"], "handlers": ["NOTION", "GMAIL", "ZOHO"], "revenue_method": "one_time", "price_inr": 999, "margin_pct": 75, "description": "Checklist -> Notion -> Gmail, India-specific, L4-gated advice"},
    "investment_newsletter": {"id": "investment_newsletter", "label": "Investment Newsletter", "tier": "F", "group": "finance", "autonomy_pct": 92, "worldwide_usd_b": 4, "india_usd_b": 0.25, "capabilities": ["email", "invoicing"], "handlers": ["TAVILY", "FRANKFURTER", "GMAIL", "ZOHO"], "revenue_method": "mandate", "price_inr": 499, "margin_pct": 85, "description": "Tavily + Frankfurter -> Gmail newsletter, Zoho mandate"},
    "api_aggregator": {"id": "api_aggregator", "label": "API Aggregator", "tier": "F", "group": "finance", "autonomy_pct": 88, "worldwide_usd_b": 12, "india_usd_b": 0.60, "capabilities": ["email", "invoicing", "payment_processing"], "handlers": ["TAVILY", "ZOHO", "GITHUB"], "revenue_method": "mandate", "price_inr": 999, "margin_pct": 80, "description": "Wrap 3 free APIs -> one paid Zoho-billed API"},
}


def list_categories(group: str | None = None) -> list[dict]:
    items = list(CATEGORIES.values())
    if group:
        items = [c for c in items if c["group"] == group]
    return sorted(items, key=lambda c: (-c["autonomy_pct"], -c["worldwide_usd_b"]))


def get_category(cid: str) -> dict | None:
    return CATEGORIES.get(cid)


def zoho_coverage_for(category_id: str) -> dict:
    """Is this category fully Zoho-billable without extra config?"""
    cat = CATEGORIES.get(category_id)
    if not cat:
        return {"covered": False, "reason": "unknown category"}
    method = cat.get("revenue_method")
    if method in ("one_time", "mandate", "invoice"):
        return {"covered": True, "via": "zoho_client (Payments + Books)", "method": method}
    if method == "affiliate":
        return {"covered": False, "via": "external affiliate network", "note": "Zoho only for accounting, not collection"}
    return {"covered": True, "via": "zoho_client", "method": method}


def autonomy_report(category_id: str) -> dict:
    cat = CATEGORIES.get(category_id)
    if not cat:
        return {"error": "unknown category"}
    needs_composio = any(h in ("GOOGLECALENDAR", "SHOPIFY", "JIRA", "HUBSPOT") for h in cat.get("handlers", []))
    return {
        "category": cat["id"],
        "autonomy_pct": cat["autonomy_pct"],
        "handlers": cat["handlers"],
        "needs_composio": needs_composio,
        "zoho": zoho_coverage_for(category_id),
        "revenue_inr": cat.get("price_inr"),
    }


if __name__ == "__main__":
    assert len(CATEGORIES) == 50, len(CATEGORIES)
    print(f"OK — {len(CATEGORIES)} categories, {len([c for c in CATEGORIES.values() if c['autonomy_pct'] >= 90])} GREEN>=90%")
