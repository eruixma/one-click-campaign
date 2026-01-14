"""Pega When Rule data models."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Comparator(str, Enum):
    """Pega When Rule comparators - both simple and function-based."""
    # Simple comparators (used in rule builder UI)
    EQUALS = "is equal to"
    NOT_EQUALS = "is not equal to"
    GREATER_THAN = "is greater than"
    GREATER_THAN_OR_EQUAL = "is greater than or equal to"
    LESS_THAN = "is less than"
    LESS_THAN_OR_EQUAL = "is less than or equal to"
    IS_TRUE = "is true"
    IS_FALSE = "is false"
    IS_BLANK = "is blank"
    IS_NOT_BLANK = "is not blank"
    CONTAINS = "contains"
    STARTS_WITH = "starts with"
    ENDS_WITH = "ends with"
    IS_IN = "is in"
    IS_NOT_IN = "is not in"


class PegaFunction(str, Enum):
    """Pega built-in functions for expression syntax."""
    # String comparisons (case-insensitive)
    EQUALS_IGNORE_CASE = "@equalsIgnoreCase"
    NOT_EQUALS_IGNORE_CASE = "@notEqualsIgnoreCase"
    CONTAINS = "@contains"
    STARTS_WITH = "@startsWith"
    ENDS_WITH = "@endsWith"

    # Numeric comparisons
    GREATER_THAN = "@greaterThan"
    GREATER_THAN_OR_EQUAL = "@greaterThanOrEqual"
    LESS_THAN = "@lessThan"
    LESS_THAN_OR_EQUAL = "@lessThanOrEqual"

    # String manipulation
    TRIM = "@trim"

    # Boolean checks
    IS_TRUE = "@isTrue"
    IS_FALSE = "@isFalse"
    IS_BLANK = "@isBlank"
    IS_NOT_BLANK = "@isNotBlank"

    # Utility
    CALL_WHEN = "@Utilities.callWhen"
    IS_IN_PAGE_LIST = "@IsInPageListWhen"


class LogicalOperator(str, Enum):
    """Logical operators to combine conditions."""
    AND = "AND"
    OR = "OR"


class ConditionType(str, Enum):
    """Type of condition."""
    PROPERTY_COMPARISON = "property"
    RULE_REFERENCE = "rule"
    FUNCTION_CALL = "function"


class Condition(BaseModel):
    """A single condition in a Pega When Rule.

    Supports three types:
    1. Property comparison: AGE_NUM > 18, CUST_SEGMENT == "Premier"
    2. Rule reference: {Rule IsValidRPQ evaluates to true}
    3. Function call: @equalsIgnoreCase(@trim(PROP), "value")
    """
    condition_type: ConditionType = Field(
        default=ConditionType.PROPERTY_COMPARISON,
        description="Type of condition"
    )

    # For property comparisons
    property_reference: Optional[str] = Field(
        default=None,
        description="Property name (e.g., AGE_NUM, CUST_CTRY_RELN_CDE10)"
    )
    comparator: Optional[Comparator] = Field(
        default=None,
        description="Comparison operator for simple syntax"
    )
    pega_function: Optional[PegaFunction] = Field(
        default=None,
        description="Pega function for expression syntax"
    )
    compare_value: Optional[str] = Field(
        default=None,
        description="Value to compare against"
    )
    apply_trim: bool = Field(
        default=True,
        description="Whether to apply @trim() to the property"
    )
    compare_value_is_property: bool = Field(
        default=False,
        description="True if compare_value is a property reference"
    )

    # For rule references
    referenced_rule: Optional[str] = Field(
        default=None,
        description="Name of the When rule to reference"
    )
    rule_evaluates_to: bool = Field(
        default=True,
        description="Expected evaluation result of referenced rule"
    )


class ConditionGroup(BaseModel):
    """A group of conditions combined with a logical operator."""
    conditions: list[Condition] = Field(
        description="List of conditions in this group"
    )
    operator: LogicalOperator = Field(
        default=LogicalOperator.AND,
        description="Logical operator to combine conditions (AND/OR)"
    )


class WhenRule(BaseModel):
    """A Pega When Rule definition.

    When rules evaluate boolean expressions to return true or false.
    They are used for visibility conditions, routing logic, validation,
    exclusions, and campaign targeting criteria.
    """
    rule_name: str = Field(
        description="Name of the when rule. Example: IsEligibleForCampaign_47817"
    )
    applies_to: str = Field(
        description="The class/context. Example: Customer Eligibility, Bond Products"
    )
    description: str = Field(
        description="Brief description of what this rule evaluates"
    )
    condition_groups: list[ConditionGroup] = Field(
        description="Groups of conditions"
    )
    group_operator: LogicalOperator = Field(
        default=LogicalOperator.AND,
        description="Operator to combine condition groups"
    )
    campaign_id: Optional[str] = Field(
        default=None,
        description="Campaign ID suffix (e.g., 47817)"
    )

    def to_expression(self, use_pega_functions: bool = True) -> str:
        """Convert the When Rule to a Pega expression string.

        Args:
            use_pega_functions: If True, use @function() syntax. If False, use simple syntax.
        """
        group_expressions = []
        op_symbol = "&&" if self.group_operator == LogicalOperator.AND else "||"

        for group in self.condition_groups:
            conditions_str = []
            for cond in group.conditions:
                expr = self._condition_to_expr(cond, use_pega_functions)
                conditions_str.append(expr)

            group_op = "&&" if group.operator == LogicalOperator.AND else "||"

            if len(conditions_str) == 1:
                group_expressions.append(conditions_str[0])
            else:
                joined = f" {group_op} ".join(conditions_str)
                group_expressions.append(f"({joined})")

        if len(group_expressions) == 1:
            return group_expressions[0]
        return f" {op_symbol} ".join(group_expressions)

    def _condition_to_expr(self, cond: Condition, use_pega_functions: bool) -> str:
        """Convert a single condition to expression string."""

        # Rule reference
        if cond.condition_type == ConditionType.RULE_REFERENCE and cond.referenced_rule:
            eval_str = "true" if cond.rule_evaluates_to else "false"
            return f"{{Rule {cond.referenced_rule} evaluates to {eval_str}}}"

        # Property comparison
        prop = cond.property_reference or ""

        if use_pega_functions and cond.pega_function:
            return self._build_function_expr(cond)

        if use_pega_functions:
            return self._build_function_expr_from_comparator(cond)

        # Simple syntax
        if cond.comparator:
            comp = cond.comparator.value
            if cond.comparator in (Comparator.IS_TRUE, Comparator.IS_FALSE,
                                   Comparator.IS_BLANK, Comparator.IS_NOT_BLANK):
                return f"{prop} {comp}"

            val = cond.compare_value
            if not cond.compare_value_is_property and isinstance(val, str):
                if not val.startswith('"') and not val.replace('.', '').replace('-', '').isdigit():
                    val = f'"{val}"'
            return f"{prop} {comp} {val}"

        return prop

    def _build_function_expr(self, cond: Condition) -> str:
        """Build expression using specified Pega function."""
        prop = cond.property_reference or ""
        func = cond.pega_function

        if cond.apply_trim and func not in (PegaFunction.GREATER_THAN, PegaFunction.LESS_THAN,
                                             PegaFunction.GREATER_THAN_OR_EQUAL, PegaFunction.LESS_THAN_OR_EQUAL):
            prop = f"@trim({prop})"

        if func in (PegaFunction.IS_TRUE, PegaFunction.IS_FALSE,
                    PegaFunction.IS_BLANK, PegaFunction.IS_NOT_BLANK):
            return f"{func.value}({prop})"

        val = cond.compare_value or ""
        if not cond.compare_value_is_property and not val.startswith('"'):
            if not val.replace('.', '').replace('-', '').isdigit():
                val = f'"{val}"'

        return f"{func.value}({prop}, {val})"

    def _build_function_expr_from_comparator(self, cond: Condition) -> str:
        """Build Pega function expression from simple comparator."""
        prop = cond.property_reference or ""
        comp = cond.comparator
        val = cond.compare_value or ""

        # Map comparators to functions
        func_map = {
            Comparator.EQUALS: PegaFunction.EQUALS_IGNORE_CASE,
            Comparator.NOT_EQUALS: PegaFunction.NOT_EQUALS_IGNORE_CASE,
            Comparator.GREATER_THAN: PegaFunction.GREATER_THAN,
            Comparator.GREATER_THAN_OR_EQUAL: PegaFunction.GREATER_THAN_OR_EQUAL,
            Comparator.LESS_THAN: PegaFunction.LESS_THAN,
            Comparator.LESS_THAN_OR_EQUAL: PegaFunction.LESS_THAN_OR_EQUAL,
            Comparator.CONTAINS: PegaFunction.CONTAINS,
            Comparator.STARTS_WITH: PegaFunction.STARTS_WITH,
            Comparator.ENDS_WITH: PegaFunction.ENDS_WITH,
            Comparator.IS_TRUE: PegaFunction.IS_TRUE,
            Comparator.IS_FALSE: PegaFunction.IS_FALSE,
            Comparator.IS_BLANK: PegaFunction.IS_BLANK,
            Comparator.IS_NOT_BLANK: PegaFunction.IS_NOT_BLANK,
        }

        func = func_map.get(comp)
        if not func:
            # Fallback to simple comparison
            return f"({prop} == {val})"

        # Apply trim for string comparisons
        is_numeric = comp in (Comparator.GREATER_THAN, Comparator.LESS_THAN,
                              Comparator.GREATER_THAN_OR_EQUAL, Comparator.LESS_THAN_OR_EQUAL)

        if cond.apply_trim and not is_numeric:
            prop = f"@trim({prop})"

        if func in (PegaFunction.IS_TRUE, PegaFunction.IS_FALSE,
                    PegaFunction.IS_BLANK, PegaFunction.IS_NOT_BLANK):
            return f"{func.value}({prop})"

        # Quote string values for non-numeric comparisons
        if not is_numeric and not val.startswith('"'):
            if not val.replace('.', '').replace('-', '').isdigit():
                val = f'"{val}"'

        return f"{func.value}({prop}, {val})"

    def to_pega_xml(self) -> str:
        """Generate Pega-compatible XML representation of the When Rule."""
        conditions_xml = []

        for group_idx, group in enumerate(self.condition_groups):
            for cond_idx, cond in enumerate(group.conditions):
                if cond.condition_type == ConditionType.RULE_REFERENCE:
                    condition_xml = f"""    <ruleReference>
      <ruleName>{cond.referenced_rule}</ruleName>
      <evaluatesTo>{str(cond.rule_evaluates_to).lower()}</evaluatesTo>
    </ruleReference>"""
                else:
                    condition_xml = f"""    <condition>
      <propertyRef>{cond.property_reference or ""}</propertyRef>
      <comparator>{cond.comparator.value if cond.comparator else ""}</comparator>
      <compareValue>{cond.compare_value or ""}</compareValue>
      <compareValueIsProperty>{str(cond.compare_value_is_property).lower()}</compareValueIsProperty>
    </condition>"""
                conditions_xml.append(condition_xml)

                if cond_idx < len(group.conditions) - 1:
                    op = "&&" if group.operator == LogicalOperator.AND else "||"
                    conditions_xml.append(f"    <operator>{op}</operator>")

            if group_idx < len(self.condition_groups) - 1:
                op = "&&" if self.group_operator == LogicalOperator.AND else "||"
                conditions_xml.append(f"    <groupOperator>{op}</groupOperator>")

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<pega:WhenRule xmlns:pega="http://www.pega.com/rules">
  <ruleName>{self.rule_name}</ruleName>
  <appliesTo>{self.applies_to}</appliesTo>
  <description>{self.description}</description>
  <campaignId>{self.campaign_id or ""}</campaignId>
  <conditions>
{chr(10).join(conditions_xml)}
  </conditions>
</pega:WhenRule>"""

    def to_dict(self) -> dict:
        """Convert to dictionary format suitable for Pega REST API."""
        conditions_list = []
        for group in self.condition_groups:
            for cond in group.conditions:
                if cond.condition_type == ConditionType.RULE_REFERENCE:
                    conditions_list.append({
                        "pyConditionType": "rule",
                        "pyRuleName": cond.referenced_rule,
                        "pyEvaluatesTo": cond.rule_evaluates_to,
                        "pyLogicalOperator": "&&" if group.operator == LogicalOperator.AND else "||"
                    })
                else:
                    conditions_list.append({
                        "pyConditionType": "property",
                        "pyPropertyRef": cond.property_reference or "",
                        "pyComparator": cond.comparator.value if cond.comparator else "",
                        "pyCompareValue": cond.compare_value or "",
                        "pyCompareValueIsProperty": cond.compare_value_is_property,
                        "pyLogicalOperator": "&&" if group.operator == LogicalOperator.AND else "||"
                    })

        return {
            "pxObjClass": "Rule-Obj-When",
            "pyClassName": self.applies_to,
            "pyRuleName": self.rule_name,
            "pyDescription": self.description,
            "pyCampaignId": self.campaign_id,
            "pyConditions": conditions_list
        }
