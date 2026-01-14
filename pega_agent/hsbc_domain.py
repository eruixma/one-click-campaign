"""HSBC RBWM Domain-specific data models and metadata.

This module defines the analytical record tables used in HSBC Retail Banking
and Wealth Management for campaign targeting and decision management.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DataGranularity(str, Enum):
    """Data granularity levels for analytical records."""
    CUSTOMER = "Customer Level"
    CUSTOMER_ACCOUNT = "Customer + Account Level"
    PRODUCT = "Product Level"


class RoleType(str, Enum):
    """Account role types."""
    PRIMARY = "Primary"
    SECONDARY = "Secondary"


class RuleCategory(str, Enum):
    """Categories of When Rules."""
    ELIGIBILITY = "Customer Eligibility"
    EXCLUSION = "Exclusion"
    PRODUCT = "Bond Products"
    TARGETING = "Targeting"


@dataclass
class AnalyticalRecordTable:
    """Metadata for an analytical record table."""
    name: str
    full_name: str
    scope: str
    granularity: DataGranularity
    keys: list[str]
    variable_summary: str
    technical_criteria: Optional[str] = None
    pega_class: Optional[str] = None


# HSBC RBWM Analytical Record Tables
CAR_TABLE = AnalyticalRecordTable(
    name="CAR",
    full_name="Customer Analytical Record",
    scope="HSBC RBWM Customer",
    granularity=DataGranularity.CUSTOMER,
    keys=["PseudoCustomerID"],
    variable_summary="CAR_Summary",
    technical_criteria="BK_SECTR = 'P' AND BK_ID = 4 AND CUST_IDC = 'Y'",
    pega_class="HSBC-Data-CAR",
)

AAR_TABLE = AnalyticalRecordTable(
    name="AAR",
    full_name="Account Analytical Record",
    scope="HSBC RBWM Customer Related Primary & Secondary Account Records",
    granularity=DataGranularity.CUSTOMER_ACCOUNT,
    keys=["PseudoCustomerID", "PseudoAccountID", "RoleType"],
    variable_summary="AAR_Summary",
    pega_class="HSBC-Data-AAR",
)

MAR_TABLE = AnalyticalRecordTable(
    name="MAR",
    full_name="Modeling Analytical Record",
    scope="HSBC RBWM Customer Related Modeling Records",
    granularity=DataGranularity.CUSTOMER,
    keys=["PseudoCustomerID"],
    variable_summary="MAR_Summary",
    pega_class="HSBC-Data-MAR",
)

ALL_TABLES = [CAR_TABLE, AAR_TABLE, MAR_TABLE]


# ============================================================================
# PEGA PROPERTY DEFINITIONS (UPPERCASE_SNAKE_CASE format)
# These match the actual property names used in Pega rules
# ============================================================================

# Customer Eligibility Properties
CUSTOMER_ELIGIBILITY_PROPERTIES = {
    # Demographics & Identity
    "AGE_NUM": "Customer's age in years",
    "CUST_CTRY_RELN_CDE8": "Customer country relation code (8-char)",
    "CUST_CTRY_RELN_CDE10": "Customer country relation code (10-char)",

    # Suppression Codes (marketing preferences)
    "CUST_SUPRS_CDE2": "Suppression code 2 (e.g., CPEXCL)",
    "CUST_SUPRS_CDE18": "Suppression code 18 (e.g., NOMK8K - no marketing)",
    "CUST_SUPRS_CDE36": "Suppression code 36 (e.g., F_SANT)",

    # Segmentation
    "Cust_Seg_Schem_Cde10": "Customer segment scheme code",
    "CUST_SEGMENT": "Customer segment (Mass, Premier, etc.)",

    # Compliance & Risk
    "CUST_RISK_VAL": "Customer risk value (1-5 scale)",
    "KYC_STATUS": "KYC verification status",
    "AML_FLAG": "AML flag indicator",
}

# Investment & Bond Product Properties
INVESTMENT_PROPERTIES = {
    # RPQ (Risk Profile Questionnaire)
    "RPQ_STATUS": "RPQ validity status (Valid/Invalid/Expired)",
    "RPQ_RISK_LEVEL": "RPQ risk tolerance level (1-5)",
    "RPQ_EXPIRY_DT": "RPQ expiry date",

    # Investment Account
    "INV_ACCT_FLG": "Has investment account flag",
    "INV_ACCT_STATUS": "Investment account status",

    # Bond Holdings
    "BOND_HOLDING_CNT": "Number of bonds held",
    "BOND_CERT_DEP_MAT_NXT_2_DY_CNT": "Count of bonds maturing in next 2 days",
    "BOND_CERT_DEPST_LATE_MTUR_DT": "Latest bond maturity date",
    "BOND_TOTAL_VALUE": "Total bond holdings value",

    # Static Codes
    "STATIC_CODE_VALID": "Static code validity flag",
}

# Standard Exclusion Rules (reusable across campaigns)
STANDARD_EXCLUSION_RULES = {
    "IsCustomersHoldingMPF": "Customers holding MPF (Mandatory Provident Fund)",
    "IsMMOCustomers": "MMO (Mass Market Outbound) customers",
    "IsValidAccountAcclLevel": "Valid account at account level",
    "IsValidAccountCusLevel": "Valid account at customer level",
    "NonCreditCampaigns": "Non-credit campaign exclusion",
    "IsHKID": "Has Hong Kong ID",
    "IsTcTi": "TC/TI customer flag",
    "IsNRCCustomers": "Non-Resident Customer flag",
    "IsWelfarePayment": "Welfare payment recipients",
    "IsNationalityUSCAKR": "US/Canada/Korea nationality (FATCA)",
    "UnpreferredCustomerList": "On unpreferred customer list",
    "IsFullKYC": "Full KYC completed",
    "IsNRCCustomersTaiwan": "NRC customers - Taiwan",
    "IsHIPB": "HIPB (High Income Private Banking) customer",
    "MentalWellBeing_Ref": "Mental wellbeing reference check",
}

# Exclusion Package Definitions
EXCLUSION_PACKAGES = {
    "OfferLocal": "Standard local offer exclusions",
    "StandardExclusion": "Standard campaign exclusions (age, country, suppression)",
    "ProductSpecific": "Product-specific exclusions (per campaign)",
}

# Common CAR (Customer) properties in PascalCase format
CAR_PROPERTIES = {
    # Customer Demographics
    "CustomerAge": "Customer's age in years",
    "CustomerSegment": "Customer segment (Mass, Mass Affluent, Premier, etc.)",
    "CustomerTenure": "Years as HSBC customer",
    "CustomerTier": "Customer tier level",
    "RelationshipManager": "Assigned RM indicator",
    "IsStaff": "HSBC staff indicator",
    "CountryOfResidence": "Customer's country of residence",
    "PreferredChannel": "Preferred communication channel",

    # Customer Value
    "TotalRelationshipBalance": "Total balance across all products",
    "AverageMonthlyBalance": "Average monthly balance",
    "CustomerLifetimeValue": "Calculated CLV score",
    "RevenueContribution": "Annual revenue contribution",
    "ProfitabilityScore": "Customer profitability score",

    # Product Holdings
    "HasCurrentAccount": "Has current/checking account",
    "HasSavingsAccount": "Has savings account",
    "HasCreditCard": "Has credit card product",
    "HasMortgage": "Has mortgage product",
    "HasPersonalLoan": "Has personal loan",
    "HasInvestment": "Has investment products",
    "HasInsurance": "Has insurance products",
    "ProductCount": "Number of products held",

    # Behavioral
    "DigitalActive": "Active on digital channels",
    "MobileAppUser": "Uses mobile banking app",
    "LastLoginDays": "Days since last digital login",
    "TransactionFrequency": "Monthly transaction count",

    # Risk & Compliance
    "RiskRating": "Customer risk rating",
    "KYCStatus": "KYC verification status",
    "AMLFlag": "AML flag indicator",
}

# Common AAR (Account) properties
AAR_PROPERTIES = {
    # Account Identifiers
    "AccountType": "Type of account (Current, Savings, etc.)",
    "AccountStatus": "Account status (Active, Dormant, Closed)",
    "RoleType": "Primary or Secondary account holder",
    "AccountOpenDate": "Date account was opened",
    "AccountTenure": "Account age in months",

    # Balances
    "CurrentBalance": "Current account balance",
    "AvailableBalance": "Available balance",
    "AverageBalance3M": "3-month average balance",
    "AverageBalance6M": "6-month average balance",
    "AverageBalance12M": "12-month average balance",
    "MinBalanceMTD": "Minimum balance month-to-date",
    "MaxBalanceMTD": "Maximum balance month-to-date",

    # Transactions
    "DebitCount": "Number of debit transactions",
    "CreditCount": "Number of credit transactions",
    "DebitAmount": "Total debit amount",
    "CreditAmount": "Total credit amount",
    "LastTransactionDate": "Date of last transaction",

    # Credit (for credit products)
    "CreditLimit": "Credit limit amount",
    "CreditUtilization": "Credit utilization percentage",
    "OutstandingBalance": "Outstanding credit balance",
    "MinimumPaymentDue": "Minimum payment due",
    "PaymentDueDate": "Payment due date",
    "DaysPastDue": "Days past due",
}

# Common MAR (Modeling) properties - propensity scores and model outputs
MAR_PROPERTIES = {
    # Propensity Scores (0-1 scale typically)
    "PropensityCreditCard": "Propensity to acquire credit card",
    "PropensityPersonalLoan": "Propensity to acquire personal loan",
    "PropensityMortgage": "Propensity to acquire mortgage",
    "PropensityInvestment": "Propensity to invest",
    "PropensityInsurance": "Propensity to buy insurance",
    "PropensityDeposit": "Propensity to increase deposits",

    # Churn & Retention
    "ChurnProbability": "Probability of customer churn",
    "RetentionScore": "Customer retention score",
    "AttritionRisk": "Attrition risk level (High/Medium/Low)",

    # Response Scores
    "ResponseProbability": "Likelihood to respond to offer",
    "ConversionProbability": "Likelihood to convert",
    "EngagementScore": "Customer engagement score",

    # Segment & Classification
    "BehavioralSegment": "Behavioral segmentation cluster",
    "ValueSegment": "Value-based segment",
    "LifestageSegment": "Lifestage segment",
    "NeedsCluster": "Needs-based cluster assignment",

    # Next Best Action
    "NBARecommendation": "Next best action recommendation",
    "NBAScore": "NBA confidence score",
    "NBACategory": "NBA category (Acquire/Retain/Grow)",
}


def get_table_info() -> dict:
    """Get information about all analytical record tables."""
    return {
        "tables": [
            {
                "name": t.name,
                "full_name": t.full_name,
                "scope": t.scope,
                "granularity": t.granularity.value,
                "keys": t.keys,
                "variable_summary": t.variable_summary,
                "pega_class": t.pega_class,
                "technical_criteria": t.technical_criteria,
            }
            for t in ALL_TABLES
        ]
    }


def get_table_properties(table_name: str) -> dict:
    """Get properties for a specific analytical record table."""
    table_props = {
        "CAR": CAR_PROPERTIES,
        "AAR": AAR_PROPERTIES,
        "MAR": MAR_PROPERTIES,
        "ELIGIBILITY": CUSTOMER_ELIGIBILITY_PROPERTIES,
        "INVESTMENT": INVESTMENT_PROPERTIES,
    }

    if table_name.upper() not in table_props:
        return {"error": f"Unknown table: {table_name}. Valid: CAR, AAR, MAR, ELIGIBILITY, INVESTMENT"}

    props = table_props[table_name.upper()]
    return {
        "table": table_name.upper(),
        "properties": [
            {"name": name, "description": desc}
            for name, desc in props.items()
        ]
    }


def get_standard_exclusion_rules() -> dict:
    """Get list of standard exclusion rules that can be referenced."""
    return {
        "exclusion_rules": [
            {"rule_name": name, "description": desc}
            for name, desc in STANDARD_EXCLUSION_RULES.items()
        ],
        "usage": "Reference these rules using: {Rule <RuleName> evaluates to true}"
    }


def get_exclusion_packages() -> dict:
    """Get list of exclusion packages."""
    return {
        "packages": [
            {"name": name, "description": desc}
            for name, desc in EXCLUSION_PACKAGES.items()
        ]
    }


def suggest_data_source(property_hint: str) -> dict:
    """Suggest which data source (CAR/AAR/MAR) to use based on property context."""
    hint_lower = property_hint.lower()

    suggestions = []

    # Check for investment/bond indicators
    investment_keywords = ["bond", "rpq", "maturity", "investment account", "risk profile", "certificate"]
    if any(kw in hint_lower for kw in investment_keywords):
        suggestions.append({
            "table": "INVESTMENT",
            "reason": "Property relates to investment/bond products",
            "class": "Bond Products"
        })

    # Check for exclusion/eligibility indicators
    eligibility_keywords = ["exclusion", "eligibility", "suppression", "country code", "kyc", "compliance"]
    if any(kw in hint_lower for kw in eligibility_keywords):
        suggestions.append({
            "table": "ELIGIBILITY",
            "reason": "Property relates to customer eligibility/exclusions",
            "class": "Customer Eligibility"
        })

    # Check for account-level indicators
    account_keywords = ["account", "balance", "transaction", "credit limit", "utilization", "payment"]
    if any(kw in hint_lower for kw in account_keywords):
        suggestions.append({
            "table": "AAR",
            "reason": "Property relates to account-level data",
            "class": "HSBC-Data-AAR"
        })

    # Check for model/propensity indicators
    model_keywords = ["propensity", "score", "probability", "likelihood", "segment", "cluster", "nba", "churn", "risk"]
    if any(kw in hint_lower for kw in model_keywords):
        suggestions.append({
            "table": "MAR",
            "reason": "Property relates to model outputs or propensity scores",
            "class": "HSBC-Data-MAR"
        })

    # Check for customer-level indicators (default)
    customer_keywords = ["customer", "age", "tenure", "product", "relationship", "tier", "segment", "digital", "channel"]
    if any(kw in hint_lower for kw in customer_keywords) or not suggestions:
        suggestions.append({
            "table": "CAR",
            "reason": "Property relates to customer-level attributes",
            "class": "HSBC-Data-CAR"
        })

    return {
        "query": property_hint,
        "suggestions": suggestions,
        "recommendation": suggestions[0] if suggestions else None
    }


def get_campaign_rule_template(campaign_id: str, campaign_type: str = "bond_maturity") -> dict:
    """Get a template for campaign rules based on campaign type.

    Args:
        campaign_id: The campaign ID (e.g., "47817")
        campaign_type: Type of campaign (bond_maturity, credit_card, personal_loan, etc.)

    Returns:
        Dictionary with rule templates for the campaign
    """
    templates = {
        "bond_maturity": {
            "description": "Bond maturity reinvestment campaign",
            "universal_criteria": [
                "Has valid investment account (INV_ACCT_FLG)",
                "Holds at least one bond (BOND_HOLDING_CNT > 0)",
            ],
            "suggested_rules": [
                {
                    "name": f"OtherStandardExclusion_{campaign_id}",
                    "type": "exclusion",
                    "description": "Standard exclusion rules for the campaign",
                },
                {
                    "name": f"StandardExcl_Eligibility",
                    "type": "eligibility",
                    "description": "Standard eligibility exclusions (age, country, suppression)",
                },
                {
                    "name": f"IsValidRPQ_{campaign_id}",
                    "type": "targeting",
                    "description": "Check if customer has valid RPQ with risk level 1-5",
                },
                {
                    "name": f"IsBondMaturityInNext2Days_{campaign_id}",
                    "type": "targeting",
                    "description": "Check if bonds mature within 2 days",
                },
            ],
            "groups": [
                {
                    "name": "Group 1: Ready to Reinvest",
                    "criteria": "Valid RPQ AND multiple bonds maturing",
                },
                {
                    "name": "Group 2: Needs Nurturing (Single)",
                    "criteria": "Invalid RPQ AND exactly 1 bond maturing",
                },
                {
                    "name": "Group 3: Needs Nurturing (Multiple)",
                    "criteria": "Invalid RPQ AND multiple bonds maturing",
                },
            ],
        },
    }

    if campaign_type not in templates:
        return {"error": f"Unknown campaign type: {campaign_type}. Available: {list(templates.keys())}"}

    template = templates[campaign_type]
    template["campaign_id"] = campaign_id
    return template
