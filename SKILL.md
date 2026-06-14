---
name: agentii-investment-intelligence
version: 2.2.1
description: >-
  Institutional-grade equity research skills for AI agents. 25 Claude-type skills
  across 4 verticals (equity-research-core, business-intelligence, industry-analysis,
  models-and-pitches) powered by agentii.ai's agent-use-ready SEC filing data plane
  — 10 years of filings, XBRL financials, earnings calendars, and company profiles
  for 165+ US-public-equity tickers. Features the three-layer retrieval protocol
  (Document Discovery → Page Map → Deep Read) for ~99% token efficiency, server-side
  parallel multi-period search via search_cross_period, and a full Excel/PPT generation
  pipeline with 3-tier office backend support.
author: agentii-ai
license: Apache-2.0
homepage: https://agentii.ai
documentation: https://agentii.ai/docs
tools:
  - search_xbrl_facts
  - list_xbrl_concepts
  - search_sec_filings
  - search_documents
  - search_companies
  - search_earnings_calendar
  - list_upcoming_earnings
  - list_sources
  - read_source_outline
  - read_source_pages
  - search_keyword_in_source
  - search_cross_period
  - get_company_profile
  - get_company_financials
  - get_company_fiscal_calendar
  - list_coverage
  - get_ticker_coverage
  - list_domains
  - get_entity_knowledge
env:
  - name: AGENTII_API_KEY
    required: true
    description: Generate at https://agentii.ai/api-keys — 7-day free trial, 2,000 credits, no credit card
  - name: AGENTII_BASE_URL
    required: false
    default: https://api.agentii.ai
---
