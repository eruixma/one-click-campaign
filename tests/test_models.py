"""Tests for Pega When Rule models."""

import pytest
from pega_agent.models import (
    WhenRule,
    Condition,
    ConditionGroup,
    Comparator,
    LogicalOperator,
)


class TestCondition:
    def test_simple_condition(self):
        cond = Condition(
            property_reference=".CustomerAge",
            comparator=Comparator.GREATER_THAN,
            compare_value="18"
        )
        assert cond.property_reference == ".CustomerAge"
        assert cond.comparator == Comparator.GREATER_THAN
        assert cond.compare_value == "18"

    def test_boolean_condition(self):
        cond = Condition(
            property_reference=".IsActive",
            comparator=Comparator.IS_TRUE
        )
        assert cond.compare_value is None


class TestWhenRule:
    def test_simple_when_rule_expression(self):
        when_rule = WhenRule(
            rule_name="IsAdult",
            applies_to="MyApp-Data-Customer",
            description="Customer is an adult",
            condition_groups=[
                ConditionGroup(
                    conditions=[
                        Condition(
                            property_reference=".Age",
                            comparator=Comparator.GREATER_THAN_OR_EQUAL,
                            compare_value="18"
                        )
                    ]
                )
            ]
        )
        assert when_rule.to_expression() == '.Age is greater than or equal to 18'

    def test_and_conditions(self):
        when_rule = WhenRule(
            rule_name="IsQualified",
            applies_to="MyApp-Data-Applicant",
            description="Applicant is qualified",
            condition_groups=[
                ConditionGroup(
                    conditions=[
                        Condition(
                            property_reference=".Age",
                            comparator=Comparator.GREATER_THAN,
                            compare_value="21"
                        ),
                        Condition(
                            property_reference=".HasLicense",
                            comparator=Comparator.IS_TRUE
                        )
                    ],
                    operator=LogicalOperator.AND
                )
            ]
        )
        expr = when_rule.to_expression()
        assert ".Age is greater than 21" in expr
        assert ".HasLicense is true" in expr
        assert "AND" in expr

    def test_or_groups(self):
        when_rule = WhenRule(
            rule_name="IsVIP",
            applies_to="MyApp-Data-Customer",
            description="Customer is VIP",
            condition_groups=[
                ConditionGroup(
                    conditions=[
                        Condition(
                            property_reference=".TotalSpend",
                            comparator=Comparator.GREATER_THAN,
                            compare_value="10000"
                        )
                    ]
                ),
                ConditionGroup(
                    conditions=[
                        Condition(
                            property_reference=".Tier",
                            comparator=Comparator.EQUALS,
                            compare_value="Platinum"
                        )
                    ]
                )
            ],
            group_operator=LogicalOperator.OR
        )
        expr = when_rule.to_expression()
        assert "OR" in expr

    def test_to_pega_xml(self):
        when_rule = WhenRule(
            rule_name="IsActive",
            applies_to="MyApp-Data-Account",
            description="Account is active",
            condition_groups=[
                ConditionGroup(
                    conditions=[
                        Condition(
                            property_reference=".Status",
                            comparator=Comparator.EQUALS,
                            compare_value="Active"
                        )
                    ]
                )
            ]
        )
        xml = when_rule.to_pega_xml()
        assert "<ruleName>IsActive</ruleName>" in xml
        assert "<appliesTo>MyApp-Data-Account</appliesTo>" in xml
        assert "<propertyRef>.Status</propertyRef>" in xml

    def test_to_dict(self):
        when_rule = WhenRule(
            rule_name="TestRule",
            applies_to="MyApp-Data-Test",
            description="Test rule",
            condition_groups=[
                ConditionGroup(
                    conditions=[
                        Condition(
                            property_reference=".Value",
                            comparator=Comparator.EQUALS,
                            compare_value="test"
                        )
                    ]
                )
            ]
        )
        d = when_rule.to_dict()
        assert d["pxObjClass"] == "Rule-Obj-When"
        assert d["pyClassName"] == "MyApp-Data-Test"
        assert d["pyRuleName"] == "TestRule"
        assert len(d["pyConditions"]) == 1


class TestComparator:
    def test_all_comparators_have_values(self):
        for comp in Comparator:
            assert comp.value is not None
            assert len(comp.value) > 0

    def test_comparator_values(self):
        assert Comparator.EQUALS.value == "is equal to"
        assert Comparator.GREATER_THAN.value == "is greater than"
        assert Comparator.CONTAINS.value == "contains"
