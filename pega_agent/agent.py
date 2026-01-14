"""Pega When Rule Agent using Google Agent Development Kit."""

import json
from typing import Optional
from google.adk.agents import Agent

from pega_agent.models import (
    WhenRule,
    Condition,
    ConditionGroup,
    ConditionType,
    Comparator,
    LogicalOperator,
)
from pega_agent.hsbc_domain import (
    get_table_info,
    get_table_properties,
    suggest_data_source,
    get_standard_exclusion_rules,
    get_campaign_rule_template,
    CAR_TABLE,
    AAR_TABLE,
    MAR_TABLE,
    STANDARD_EXCLUSION_RULES,
)


# Real-world example When Rules based on actual HSBC campaigns
EXAMPLE_WHEN_RULES = [
    # =========================================================================
    # EXCLUSION RULES
    # =========================================================================
    {
        "input": "Standard exclusion for campaign 47817 - combine all standard exclusion rules",
        "output": WhenRule(
            rule_name="OtherStandardExclusion_47817",
            applies_to="Customer Eligibility",
            description="Standard exclusion rules combined with OR logic",
            campaign_id="47817",
            condition_groups=[
                ConditionGroup(
                    conditions=[
                        Condition(condition_type=ConditionType.RULE_REFERENCE, referenced_rule="IsCustomersHoldingMPF"),
                        Condition(condition_type=ConditionType.RULE_REFERENCE, referenced_rule="IsMMOCustomers"),
                        Condition(condition_type=ConditionType.RULE_REFERENCE, referenced_rule="IsValidAccountAcclLevel"),
                        Condition(condition_type=ConditionType.RULE_REFERENCE, referenced_rule="IsValidAccountCusLevel"),
                        Condition(condition_type=ConditionType.RULE_REFERENCE, referenced_rule="NonCreditCampaigns"),
                        Condition(condition_type=ConditionType.RULE_REFERENCE, referenced_rule="IsHKID"),
                    ],
                    operator=LogicalOperator.OR
                )
            ]
        )
    },
    {
        "input": "Standard eligibility exclusion - exclude customers from US, under 18, over 65, or with suppression codes",
        "output": WhenRule(
            rule_name="StandardExcl_Eligibility",
            applies_to="Customer Eligibility",
            description="Standard eligibility exclusions for age, country, suppression codes",
            condition_groups=[
                ConditionGroup(
                    conditions=[
                        Condition(
                            property_reference="CUST_CTRY_RELN_CDE10",
                            comparator=Comparator.EQUALS,
                            compare_value="USP"
                        ),
                        Condition(
                            property_reference="CUST_SUPRS_CDE36",
                            comparator=Comparator.EQUALS,
                            compare_value="F_SANT"
                        ),
                        Condition(
                            property_reference="AGE_NUM",
                            comparator=Comparator.LESS_THAN,
                            compare_value="18",
                            apply_trim=False
                        ),
                        Condition(
                            property_reference="CUST_SUPRS_CDE2",
                            comparator=Comparator.EQUALS,
                            compare_value="CPEXCL"
                        ),
                        Condition(
                            property_reference="AGE_NUM",
                            comparator=Comparator.GREATER_THAN,
                            compare_value="65",
                            apply_trim=False
                        ),
                    ],
                    operator=LogicalOperator.OR
                )
            ]
        )
    },
    # =========================================================================
    # BOND MATURITY CAMPAIGN RULES
    # =========================================================================
    {
        "input": "Exclude non-HK residents, check valid static code, risk value 1-5, and more than 1 bond maturing in 2 days",
        "output": WhenRule(
            rule_name="ExclNonResidencyInHK",
            applies_to="Bond Products",
            description="Non-HK resident exclusion with valid codes and bond maturity check",
            condition_groups=[
                ConditionGroup(
                    conditions=[
                        Condition(
                            property_reference="CUST_CTRY_RELN_CDE8",
                            comparator=Comparator.NOT_EQUALS,
                            compare_value="NRHK"
                        ),
                        Condition(condition_type=ConditionType.RULE_REFERENCE, referenced_rule="IsValidStaticCode"),
                        Condition(condition_type=ConditionType.RULE_REFERENCE, referenced_rule="IsCustRiskValueIn1to5"),
                        Condition(
                            property_reference="BOND_CERT_DEP_MAT_NXT_2_DY_CNT",
                            comparator=Comparator.GREATER_THAN,
                            compare_value="1",
                            apply_trim=False
                        ),
                    ],
                    operator=LogicalOperator.AND
                )
            ]
        )
    },
    {
        "input": "Check if customer has bonds maturing in the next 2 days",
        "output": WhenRule(
            rule_name="IsBondMaturityInLast2Days",
            applies_to="Bond Products",
            description="Bonds maturing within next 2 days",
            condition_groups=[
                ConditionGroup(
                    conditions=[
                        Condition(
                            property_reference="BOND_CERT_DEP_MAT_NXT_2_DY_CNT",
                            comparator=Comparator.GREATER_THAN,
                            compare_value="0",
                            apply_trim=False
                        ),
                    ],
                    operator=LogicalOperator.AND
                )
            ]
        )
    },
    {
        "input": "Check if customer is marketable (no NOMK8K suppression)",
        "output": WhenRule(
            rule_name="IsMarketable",
            applies_to="Bond Products",
            description="Customer can receive marketing communications",
            condition_groups=[
                ConditionGroup(
                    conditions=[
                        Condition(
                            property_reference="CUST_SUPRS_CDE18",
                            comparator=Comparator.NOT_EQUALS,
                            compare_value="NOMK8K"
                        ),
                    ],
                    operator=LogicalOperator.AND
                )
            ]
        )
    },
    # =========================================================================
    # INVESTMENT CAMPAIGN TARGETING RULES
    # =========================================================================
    {
        "input": "Valid RPQ with risk level between 1 and 5",
        "output": WhenRule(
            rule_name="IsCustRiskValueIn1to5",
            applies_to="Customer Eligibility",
            description="Customer has valid RPQ with risk tolerance 1-5",
            condition_groups=[
                ConditionGroup(
                    conditions=[
                        Condition(
                            property_reference="CUST_RISK_VAL",
                            comparator=Comparator.GREATER_THAN_OR_EQUAL,
                            compare_value="1",
                            apply_trim=False
                        ),
                        Condition(
                            property_reference="CUST_RISK_VAL",
                            comparator=Comparator.LESS_THAN_OR_EQUAL,
                            compare_value="5",
                            apply_trim=False
                        ),
                    ],
                    operator=LogicalOperator.AND
                )
            ]
        )
    },
    {
        "input": "Customers with investment account and holding at least one bond",
        "output": WhenRule(
            rule_name="HasInvestmentWithBonds",
            applies_to="Bond Products",
            description="Has investment account with bond holdings",
            condition_groups=[
                ConditionGroup(
                    conditions=[
                        Condition(
                            property_reference="INV_ACCT_FLG",
                            comparator=Comparator.IS_TRUE,
                            apply_trim=False
                        ),
                        Condition(
                            property_reference="BOND_HOLDING_CNT",
                            comparator=Comparator.GREATER_THAN,
                            compare_value="0",
                            apply_trim=False
                        ),
                    ],
                    operator=LogicalOperator.AND
                )
            ]
        )
    },
    # =========================================================================
    # GROUP TARGETING (from bond maturity campaign example)
    # =========================================================================
    {
        "input": "Group 1: Ready to Reinvest - Valid RPQ AND multiple bonds maturing",
        "output": WhenRule(
            rule_name="IsReadyToReinvest_47817",
            applies_to="Bond Products",
            description="Group 1: Valid RPQ with risk 1-5 AND >1 bond maturing in 2 days",
            campaign_id="47817",
            condition_groups=[
                ConditionGroup(
                    conditions=[
                        Condition(condition_type=ConditionType.RULE_REFERENCE, referenced_rule="IsCustRiskValueIn1to5"),
                        Condition(
                            property_reference="BOND_CERT_DEP_MAT_NXT_2_DY_CNT",
                            comparator=Comparator.GREATER_THAN,
                            compare_value="1",
                            apply_trim=False
                        ),
                    ],
                    operator=LogicalOperator.AND
                )
            ]
        )
    },
    {
        "input": "Group 2: Needs Nurturing Single - Invalid RPQ AND exactly 1 bond maturing",
        "output": WhenRule(
            rule_name="IsNeedsNurturingSingle_47817",
            applies_to="Bond Products",
            description="Group 2: Invalid/expired RPQ AND exactly 1 bond maturing",
            campaign_id="47817",
            condition_groups=[
                ConditionGroup(
                    conditions=[
                        Condition(
                            condition_type=ConditionType.RULE_REFERENCE,
                            referenced_rule="IsCustRiskValueIn1to5",
                            rule_evaluates_to=False
                        ),
                        Condition(
                            property_reference="BOND_CERT_DEP_MAT_NXT_2_DY_CNT",
                            comparator=Comparator.EQUALS,
                            compare_value="1",
                            apply_trim=False
                        ),
                    ],
                    operator=LogicalOperator.AND
                )
            ]
        )
    },
]


def create_when_rule(
    rule_name: str,
    applies_to: str,
    description: str,
    conditions_json: str,
    campaign_id: str = None
) -> dict:
    """Create a Pega When Rule from the provided parameters.

    Args:
        rule_name: Name of the when rule (e.g., IsHighValueCustomer, ExclNonResidency_47817)
        applies_to: The context/class this rule applies to:
            - "Customer Eligibility" for eligibility/exclusion rules
            - "Bond Products" for investment product rules
            - "HSBC-Data-CAR" for customer-level rules
            - "HSBC-Data-AAR" for account-level rules
        description: Brief description of what this rule evaluates
        conditions_json: JSON string containing condition groups. Format:
            {
                "groups": [
                    {
                        "conditions": [
                            {"property": "AGE_NUM", "comparator": "is greater than", "value": "18"},
                            {"rule": "IsValidRPQ", "evaluates_to": true},
                            ...
                        ],
                        "operator": "AND"
                    }
                ],
                "group_operator": "OR"
            }
        campaign_id: Optional campaign ID suffix (e.g., "47817")

    Returns:
        Dictionary containing the When Rule in multiple formats (expression, XML, API dict)
    """
    try:
        conditions_data = json.loads(conditions_json)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON in conditions: {e}"}

    # Build condition groups
    condition_groups = []
    for group_data in conditions_data.get("groups", []):
        conditions = []
        for cond in group_data.get("conditions", []):
            # Check if this is a rule reference
            if "rule" in cond:
                conditions.append(Condition(
                    condition_type=ConditionType.RULE_REFERENCE,
                    referenced_rule=cond.get("rule"),
                    rule_evaluates_to=cond.get("evaluates_to", True)
                ))
            else:
                # Property comparison
                comp_str = cond.get("comparator", "is equal to")
                comparator = None
                for c in Comparator:
                    if c.value == comp_str:
                        comparator = c
                        break
                if not comparator:
                    comparator = Comparator.EQUALS

                # Determine if we should apply trim (not for numeric comparisons)
                apply_trim = comparator not in (
                    Comparator.GREATER_THAN, Comparator.LESS_THAN,
                    Comparator.GREATER_THAN_OR_EQUAL, Comparator.LESS_THAN_OR_EQUAL
                )

                conditions.append(Condition(
                    condition_type=ConditionType.PROPERTY_COMPARISON,
                    property_reference=cond.get("property", ""),
                    comparator=comparator,
                    compare_value=cond.get("value"),
                    apply_trim=cond.get("apply_trim", apply_trim),
                    compare_value_is_property=cond.get("is_property", False)
                ))

        op_str = group_data.get("operator", "AND")
        operator = LogicalOperator.AND if op_str == "AND" else LogicalOperator.OR

        condition_groups.append(ConditionGroup(
            conditions=conditions,
            operator=operator
        ))

    group_op_str = conditions_data.get("group_operator", "AND")
    group_operator = LogicalOperator.AND if group_op_str == "AND" else LogicalOperator.OR

    # Create the When Rule
    when_rule = WhenRule(
        rule_name=rule_name,
        applies_to=applies_to,
        description=description,
        condition_groups=condition_groups,
        group_operator=group_operator,
        campaign_id=campaign_id
    )

    return {
        "status": "success",
        "rule_name": when_rule.rule_name,
        "applies_to": when_rule.applies_to,
        "campaign_id": when_rule.campaign_id,
        "expression": when_rule.to_expression(use_pega_functions=True),
        "expression_simple": when_rule.to_expression(use_pega_functions=False),
        "xml": when_rule.to_pega_xml(),
        "api_payload": when_rule.to_dict()
    }


def validate_when_rule(expression: str) -> dict:
    """Validate a Pega When Rule expression for syntax errors.

    Args:
        expression: The When Rule expression to validate

    Returns:
        Dictionary with validation result and any errors found
    """
    errors = []

    # Check for balanced parentheses
    if expression.count("(") != expression.count(")"):
        errors.append("Unbalanced parentheses in expression")

    # Check for balanced braces (rule references)
    if expression.count("{") != expression.count("}"):
        errors.append("Unbalanced braces in rule references")

    # Check for dangling operators
    if expression.strip().endswith(("&&", "||", "AND", "OR")):
        errors.append("Expression ends with a dangling logical operator")

    # Check for valid function syntax
    if "@" in expression:
        # Basic check for function calls
        import re
        func_pattern = r'@\w+\([^)]*\)'
        if not re.search(func_pattern, expression):
            errors.append("Invalid function syntax detected")

    return {
        "valid": len(errors) == 0,
        "expression": expression,
        "errors": errors if errors else None
    }


def list_comparators() -> dict:
    """List all available Pega When Rule comparators.

    Returns:
        Dictionary with all available comparators and their descriptions
    """
    return {
        "comparators": [
            {"value": c.value, "name": c.name}
            for c in Comparator
        ]
    }


def get_example_rules() -> dict:
    """Get example When Rules to demonstrate the expected format.

    Returns:
        Dictionary with example natural language inputs and their When Rule outputs
    """
    examples = []
    for ex in EXAMPLE_WHEN_RULES:
        examples.append({
            "natural_language": ex["input"],
            "expression": ex["output"].to_expression(),
            "rule_name": ex["output"].rule_name,
            "applies_to": ex["output"].applies_to,
            "campaign_id": ex["output"].campaign_id
        })
    return {"examples": examples}


def get_data_sources() -> dict:
    """Get information about available HSBC analytical record data sources.

    Returns information about CAR, AAR, and MAR tables including:
    - Table name and full name
    - Scope and data granularity
    - Key fields
    - Pega class to use in applies_to

    Returns:
        Dictionary with all available data sources
    """
    return get_table_info()


def get_properties_for_table(table_name: str) -> dict:
    """Get available properties for a specific data source table.

    Args:
        table_name: The table name - one of:
            - CAR: Customer Analytical Record (customer-level data)
            - AAR: Account Analytical Record (account-level data)
            - MAR: Modeling Analytical Record (propensity scores, model outputs)
            - ELIGIBILITY: Customer eligibility properties (AGE_NUM, CUST_SUPRS_CDE*, etc.)
            - INVESTMENT: Investment/bond properties (RPQ, bond maturity, etc.)

    Returns:
        Dictionary with property names and descriptions for the specified table
    """
    return get_table_properties(table_name)


def recommend_data_source(context: str) -> dict:
    """Recommend which data source to use based on the business context.

    Args:
        context: Natural language description of what data is needed.
                 Examples: "customer age and segment", "account balance",
                 "propensity to buy credit card", "bond maturity", "RPQ status"

    Returns:
        Dictionary with recommended data source(s) and reasoning
    """
    return suggest_data_source(context)


def get_exclusion_rules() -> dict:
    """Get list of standard exclusion rules that can be referenced in campaigns.

    These are pre-defined rules that handle common exclusion scenarios like:
    - MPF customers, MMO customers
    - Account validity checks
    - HKID, nationality, NRC status
    - KYC and compliance checks

    Returns:
        Dictionary with exclusion rule names and descriptions
    """
    return get_standard_exclusion_rules()


def get_campaign_template(campaign_id: str, campaign_type: str = "bond_maturity") -> dict:
    """Get a template for campaign rules based on campaign type.

    Args:
        campaign_id: The campaign ID (e.g., "47817")
        campaign_type: Type of campaign. Currently supported:
            - "bond_maturity": Bond maturity reinvestment campaigns

    Returns:
        Dictionary with suggested rule templates and targeting groups
    """
    return get_campaign_rule_template(campaign_id, campaign_type)


# Build the instruction with HSBC domain knowledge and real examples
def _build_instruction() -> str:
    examples_text = ""
    for ex in EXAMPLE_WHEN_RULES[:6]:  # Include key examples
        examples_text += f"""
Example:
  Input: "{ex["input"]}"
  Output:
    - rule_name: {ex["output"].rule_name}
    - applies_to: {ex["output"].applies_to}
    - expression: {ex["output"].to_expression()}
"""

    return f"""You are a Pega Platform expert assistant for HSBC Retail Banking and Wealth Management (RBWM).
You convert natural language campaign targeting criteria into Pega When Rules.

## HSBC Data Sources & Rule Categories

### Rule Categories (applies_to values)
- **Customer Eligibility**: Eligibility and exclusion rules (age, country, suppression codes)
- **Bond Products**: Investment and bond product targeting rules
- **HSBC-Data-CAR**: Customer-level attributes
- **HSBC-Data-AAR**: Account-level attributes
- **HSBC-Data-MAR**: Model outputs and propensity scores

### Key Property Naming Convention
Properties use UPPERCASE_SNAKE_CASE format:
- AGE_NUM: Customer age
- CUST_CTRY_RELN_CDE10: Country relation code
- CUST_SUPRS_CDE18: Suppression code (e.g., NOMK8K = no marketing)
- CUST_RISK_VAL: Risk value (1-5 scale for RPQ)
- BOND_CERT_DEP_MAT_NXT_2_DY_CNT: Bonds maturing in next 2 days
- INV_ACCT_FLG: Investment account flag

### Expression Syntax
Use Pega function syntax for expressions:
- String comparison: `@equalsIgnoreCase(@trim(PROP), "value")`
- Negative comparison: `@notEqualsIgnoreCase(@trim(PROP), "value")`
- Numeric comparison: `@greaterThan(PROP, value)`, `@lessThan(PROP, value)`
- Boolean checks: `@isTrue(PROP)`, `@isFalse(PROP)`
- Rule reference: `{{Rule RuleName evaluates to true}}`

### Logical Operators
- Use `&&` for AND
- Use `||` for OR
- Group with parentheses: `(cond1 && cond2) || (cond3 && cond4)`

## Standard Exclusion Rules (can be referenced)
{chr(10).join([f"- {name}: {desc}" for name, desc in list(STANDARD_EXCLUSION_RULES.items())[:8]])}

## Campaign Rule Structure
1. **OtherStandardExclusion_[ID]**: Combines standard exclusion rules with OR logic
2. **StandardExcl_Eligibility**: Age, country, suppression code checks
3. **Product-specific rules**: e.g., IsBondMaturityInLast2Days, IsMarketable
4. **Group targeting rules**: Segment customers into campaign groups

{examples_text}

## Workflow:
1. Identify the rule category (eligibility, exclusion, product, targeting)
2. Determine properties needed and their correct names
3. For exclusions, reference standard rules when appropriate
4. Use create_when_rule with proper applies_to class
5. Include campaign_id suffix for campaign-specific rules

Use get_properties_for_table("ELIGIBILITY") or get_properties_for_table("INVESTMENT") to see available properties.
Use get_exclusion_rules() to see standard exclusion rules you can reference.
"""


# Create the main agent
pega_when_rule_agent = Agent(
    name="pega_when_rule_agent",
    model="gemini-3-flash-preview",
    description="Converts natural language campaign criteria into Pega When Rules for HSBC RBWM",
    instruction=_build_instruction(),
    tools=[
        create_when_rule,
        validate_when_rule,
        list_comparators,
        get_example_rules,
        get_data_sources,
        get_properties_for_table,
        recommend_data_source,
        get_exclusion_rules,
        get_campaign_template,
    ]
)
