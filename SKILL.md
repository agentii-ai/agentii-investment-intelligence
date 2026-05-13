---
name: agentii-investment-intelligence
version: 1.0.0
description: SEC filings, clinical trials, FDA approvals, FAERS, earnings, and company-profile data for 1,000+ US-listed equities and biotech tickers. Optimized for AI agents with gold-label signal extraction, four-verb taxonomy, and page-level retrieval.
author: agentii-ai
license: MIT
homepage: https://agentii.ai
documentation: https://agentii.ai/docs
tools:
  - search_documents
  - get_company_profile
  - list_coverage
  - read_source_outline
  - read_source_pages
  - search_keyword_in_source
  - search_unified
env:
  - name: AGENTII_API_KEY
    required: true
    description: Generate at https://agentii.ai/api-keys
  - name: AGENTII_BASE_URL
    required: false
    default: https://api.agentii.ai
---
