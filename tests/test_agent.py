"""Tests for Pega When Rule Agent tools."""

import json
import pytest
from pega_agent.agent import (
    create_when_rule,
    validate_when_rule,
    list_comparators,
    get_example_rules,
)


class TestCreateWhenRule:
    def test_create_simple_rule(self):
        conditions_json = json.dumps({
            "groups": [
                {
                    "conditions": [
                        {
                            "property": ".CustomerAge",
                            "comparator": "is greater than",
                            "value": "18"
                        }
                    ],
                    "operator": "AND"
                }
            ],
            "group_operator": "AND"
        })

        result = create_when_rule(
            rule_name="IsAdult",
            applies_to="MyApp-Data-Customer",
            description="Customer is an adult",
            conditions_json=conditions_json
        )

        assert result["status"] == "success"
        assert result["rule_name"] == "IsAdult"
        assert ".CustomerAge is greater than 18" in result["expression"]
        assert "xml" in result
        assert "api_payload" in result

    def test_create_multi_condition_rule(self):
        conditions_json = json.dumps({
            "groups": [
                {
                    "conditions": [
                        {
                            "property": ".Amount",
                            "comparator": "is greater than",
                            "value": "1000"
                        },
                        {
                            "property": ".Status",
                            "comparator": "is equal to",
                            "value": "Pending"
                        }
                    ],
                    "operator": "AND"
                }
            ],
            "group_operator": "AND"
        })

        result = create_when_rule(
            rule_name="RequiresApproval",
            applies_to="MyApp-Work-Order",
            description="Order requires approval",
            conditions_json=conditions_json
        )

        assert result["status"] == "success"
        assert "AND" in result["expression"]

    def test_create_rule_with_invalid_json(self):
        result = create_when_rule(
            rule_name="TestRule",
            applies_to="MyApp-Data-Test",
            description="Test",
            conditions_json="invalid json"
        )

        assert "error" in result


class TestValidateWhenRule:
    def test_valid_expression(self):
        result = validate_when_rule(".CustomerAge is greater than 18")
        assert result["valid"] is True
        assert result["errors"] is None

    def test_missing_property_reference(self):
        result = validate_when_rule("CustomerAge is greater than 18")
        assert result["valid"] is False
        assert any("property reference" in e.lower() for e in result["errors"])

    def test_unbalanced_parentheses(self):
        result = validate_when_rule("(.Age is greater than 18")
        assert result["valid"] is False
        assert any("parenthes" in e.lower() for e in result["errors"])

    def test_dangling_operator(self):
        result = validate_when_rule(".Age is greater than 18 AND")
        assert result["valid"] is False
        assert any("dangling" in e.lower() for e in result["errors"])


class TestListComparators:
    def test_returns_all_comparators(self):
        result = list_comparators()
        assert "comparators" in result
        assert len(result["comparators"]) > 10

        comparator_names = [c["name"] for c in result["comparators"]]
        assert "EQUALS" in comparator_names
        assert "GREATER_THAN" in comparator_names
        assert "CONTAINS" in comparator_names


class TestGetExampleRules:
    def test_returns_examples(self):
        result = get_example_rules()
        assert "examples" in result
        assert len(result["examples"]) > 0

        for example in result["examples"]:
            assert "natural_language" in example
            assert "expression" in example
            assert "rule_name" in example
