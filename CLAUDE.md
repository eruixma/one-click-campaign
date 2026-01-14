# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

One-Click Campaign is an LLM agent built with Google Agent Development Kit (ADK) that converts natural language campaign targeting criteria into Pega When Rules for HSBC Retail Banking and Wealth Management (RBWM).

## Commands

```bash
# Install dependencies
pip install -e ".[dev]"

# Run interactive agent
python -m pega_agent.main

# Run single query
python -m pega_agent.main "customers with valid RPQ and bonds maturing in 2 days"

# Run with ADK dev UI
adk web pega_agent

# Run tests
pytest tests/
pytest tests/test_models.py -v
```

## Architecture

```
pega_agent/
├── models.py       # WhenRule, Condition, ConditionGroup with Pega function syntax
├── hsbc_domain.py  # HSBC data sources, properties, exclusion rules, campaign templates
├── agent.py        # Google ADK Agent with 9 tools
├── pega_syntax.py  # Pega expression syntax helpers
└── main.py         # CLI entry point
```

## Agent Tools

| Tool | Purpose |
|------|---------|
| `create_when_rule` | Generate When Rule from structured input |
| `validate_when_rule` | Validate expression syntax |
| `get_properties_for_table` | Get properties (CAR/AAR/MAR/ELIGIBILITY/INVESTMENT) |
| `get_exclusion_rules` | List standard exclusion rules to reference |
| `get_campaign_template` | Get campaign rule templates |
| `recommend_data_source` | Suggest data source based on context |

## Pega Expression Syntax

**Property naming**: `UPPERCASE_SNAKE_CASE` (e.g., `AGE_NUM`, `CUST_SUPRS_CDE18`)

**Functions**:
- `@equalsIgnoreCase(@trim(PROP), "value")` - string comparison
- `@notEqualsIgnoreCase(@trim(PROP), "value")` - negative string comparison
- `@greaterThan(PROP, value)` - numeric comparison
- `{Rule RuleName evaluates to true}` - rule reference

**Operators**: `&&` (AND), `||` (OR)

## Rule Categories (applies_to)

| Category | Use For |
|----------|---------|
| Customer Eligibility | Age, country, suppression code exclusions |
| Bond Products | Investment/bond targeting rules |
| HSBC-Data-CAR | Customer-level attributes |
| HSBC-Data-AAR | Account-level attributes |
| HSBC-Data-MAR | Propensity scores, model outputs |

## Key Properties

**Eligibility**: `AGE_NUM`, `CUST_CTRY_RELN_CDE10`, `CUST_SUPRS_CDE*`, `CUST_RISK_VAL`

**Investment**: `INV_ACCT_FLG`, `BOND_HOLDING_CNT`, `BOND_CERT_DEP_MAT_NXT_2_DY_CNT`, `RPQ_STATUS`

## Standard Exclusion Rules

Rules that can be referenced: `IsCustomersHoldingMPF`, `IsMMOCustomers`, `IsHKID`, `IsNRCCustomers`, `IsNationalityUSCAKR`, `UnpreferredCustomerList`, etc.

## Environment Setup

Copy `.env.example` to `.env` and set `GOOGLE_API_KEY`.
