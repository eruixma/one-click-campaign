"""Pega expression syntax and function definitions.

This module defines the actual Pega expression syntax used in When Rules,
including functions like @equalsIgnoreCase, @greaterThan, @trim, etc.
"""

from enum import Enum
from typing import Optional
from dataclasses import dataclass


class PegaFunction(str, Enum):
    """Pega built-in functions for When Rule expressions."""

    # String comparisons
    EQUALS_IGNORE_CASE = "@equalsIgnoreCase"
    NOT_EQUALS_IGNORE_CASE = "@notEqualsIgnoreCase"
    CONTAINS = "@contains"
    STARTS_WITH = "@startsWith"
    ENDS_WITH = "@endsWith"

    # String manipulation
    TRIM = "@trim"
    TO_UPPER = "@toUpper"
    TO_LOWER = "@toLower"

    # Numeric comparisons
    GREATER_THAN = "@greaterThan"
    GREATER_THAN_OR_EQUAL = "@greaterThanOrEqual"
    LESS_THAN = "@lessThan"
    LESS_THAN_OR_EQUAL = "@lessThanOrEqual"
    EQUALS = "@equals"
    NOT_EQUALS = "@notEquals"

    # Date functions
    TO_DATE = "@toDate"
    DATE_TIME_DIFFERENCE = "@DateTimeDifference"
    GET_CURRENT = "@getCurrent"

    # Utility functions
    IS_IN_PAGE_LIST_WHEN = "@IsInPageListWhen"
    UTILITIES_CALL_WHEN = "@Utilities.callWhen"

    # Boolean
    IS_TRUE = "@isTrue"
    IS_FALSE = "@isFalse"
    IS_BLANK = "@isBlank"
    IS_NOT_BLANK = "@isNotBlank"


class LogicalOperator(str, Enum):
    """Logical operators for combining conditions."""
    AND = "&&"
    OR = "||"


@dataclass
class RuleReference:
    """Reference to another When Rule."""
    rule_name: str
    evaluates_to: bool = True

    def to_expression(self) -> str:
        """Convert to Pega expression format."""
        eval_str = "true" if self.evaluates_to else "false"
        return f"{{Rule {self.rule_name} evaluates to {eval_str}}}"


@dataclass
class FunctionCall:
    """A Pega function call in an expression."""
    function: PegaFunction
    arguments: list[str]

    def to_expression(self) -> str:
        """Convert to Pega expression format."""
        args_str = ", ".join(self.arguments)
        return f"{self.function.value}({args_str})"


@dataclass
class Condition:
    """A condition in a Pega When Rule expression.

    Can be either:
    - A function call comparison (e.g., @equalsIgnoreCase(@trim(PROP), "value"))
    - A simple comparison (e.g., AGE_NUM < 18)
    - A rule reference (e.g., {Rule IsValidRPQ evaluates to true})
    """
    # For function-based conditions
    function: Optional[PegaFunction] = None
    property_ref: Optional[str] = None
    compare_value: Optional[str] = None
    apply_trim: bool = False

    # For simple comparisons
    simple_operator: Optional[str] = None  # <, >, <=, >=, ==, !=

    # For rule references
    rule_reference: Optional[RuleReference] = None

    def to_expression(self) -> str:
        """Convert to Pega expression format."""
        if self.rule_reference:
            return self.rule_reference.to_expression()

        if self.simple_operator:
            # Simple comparison like AGE_NUM < 18
            return f"({self.property_ref} {self.simple_operator} {self.compare_value})"

        if self.function:
            # Function-based comparison
            prop = self.property_ref
            if self.apply_trim:
                prop = f"@trim({self.property_ref})"

            if self.function in (PegaFunction.IS_TRUE, PegaFunction.IS_FALSE,
                                 PegaFunction.IS_BLANK, PegaFunction.IS_NOT_BLANK):
                return f"{self.function.value}({prop})"

            # Quote string values
            val = self.compare_value
            if val and not val.startswith('"') and not val.isdigit():
                val = f'"{val}"'

            return f"{self.function.value}({prop}, {val})"

        return ""


@dataclass
class ConditionGroup:
    """A group of conditions combined with a logical operator."""
    conditions: list[Condition]
    operator: LogicalOperator = LogicalOperator.AND

    def to_expression(self) -> str:
        """Convert to Pega expression format."""
        if not self.conditions:
            return ""

        exprs = [c.to_expression() for c in self.conditions]
        op = f" {self.operator.value} "

        if len(exprs) == 1:
            return exprs[0]

        return f"({op.join(exprs)})"


def build_string_comparison(
    property_ref: str,
    value: str,
    ignore_case: bool = True,
    apply_trim: bool = True,
    negate: bool = False
) -> Condition:
    """Build a string comparison condition.

    Args:
        property_ref: The property to compare (e.g., CUST_CTRY_RELN_CDE10)
        value: The value to compare against
        ignore_case: Whether to use case-insensitive comparison
        apply_trim: Whether to trim the property value
        negate: Whether to negate the comparison (not equals)

    Returns:
        A Condition object
    """
    if ignore_case:
        func = PegaFunction.NOT_EQUALS_IGNORE_CASE if negate else PegaFunction.EQUALS_IGNORE_CASE
    else:
        func = PegaFunction.NOT_EQUALS if negate else PegaFunction.EQUALS

    return Condition(
        function=func,
        property_ref=property_ref,
        compare_value=value,
        apply_trim=apply_trim
    )


def build_numeric_comparison(
    property_ref: str,
    value: str,
    operator: str  # ">" , "<", ">=", "<=", "==", "!="
) -> Condition:
    """Build a numeric comparison condition.

    Args:
        property_ref: The property to compare (e.g., AGE_NUM)
        value: The numeric value to compare against
        operator: The comparison operator

    Returns:
        A Condition object
    """
    func_map = {
        ">": PegaFunction.GREATER_THAN,
        ">=": PegaFunction.GREATER_THAN_OR_EQUAL,
        "<": PegaFunction.LESS_THAN,
        "<=": PegaFunction.LESS_THAN_OR_EQUAL,
    }

    if operator in func_map:
        return Condition(
            function=func_map[operator],
            property_ref=property_ref,
            compare_value=value,
            apply_trim=False
        )
    else:
        # Use simple comparison syntax
        return Condition(
            property_ref=property_ref,
            compare_value=value,
            simple_operator=operator
        )


def build_rule_reference(rule_name: str, evaluates_to: bool = True) -> Condition:
    """Build a rule reference condition.

    Args:
        rule_name: Name of the when rule to reference
        evaluates_to: Expected evaluation result (true/false)

    Returns:
        A Condition object
    """
    return Condition(
        rule_reference=RuleReference(rule_name=rule_name, evaluates_to=evaluates_to)
    )


# Common exclusion rule property mappings
EXCLUSION_PROPERTIES = {
    # Customer exclusions
    "country_code": "CUST_CTRY_RELN_CDE10",
    "suppression_code": "CUST_SUPRS_CDE36",
    "suppression_code_2": "CUST_SUPRS_CDE2",
    "suppression_code_18": "CUST_SUPRS_CDE18",
    "age": "AGE_NUM",
    "segment_scheme": "Cust_Seg_Schem_Cde10",

    # Investment properties
    "risk_value": "CUST_RISK_VAL",
    "rpq_status": "RPQ_STATUS",
    "rpq_expiry_date": "RPQ_EXPIRY_DT",

    # Bond properties
    "bond_maturity_count": "BOND_CERT_DEP_MAT_NXT_2_DY_CNT",
    "bond_maturity_date": "BOND_CERT_DEPST_LATE_MTUR_DT",

    # Account properties
    "investment_account_flag": "INV_ACCT_FLG",
    "bond_holding_count": "BOND_HOLDING_CNT",
}


# Standard exclusion rules that can be referenced
STANDARD_EXCLUSION_RULES = [
    "IsCustomersHoldingMPF",
    "IsMMOCustomers",
    "IsValidAccountAcclLevel",
    "IsValidAccountCusLevel",
    "NonCreditCampaigns",
    "IsHKID",
    "IsTcTi",
    "IsNRCCustomers",
    "IsWelfarePayment",
    "IsNationalityUSCAKR",
    "UnpreferredCustomerList",
    "IsFullKYC",
    "IsNRCCustomersTaiwan",
    "IsHIPB",
]
