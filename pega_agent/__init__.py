"""Pega When Rule Agent - Convert natural language to Pega When Rules for HSBC RBWM."""

from pega_agent.models import WhenRule, Condition, ConditionGroup, LogicalOperator, Comparator
from pega_agent.agent import pega_when_rule_agent
from pega_agent.hsbc_domain import (
    CAR_TABLE,
    AAR_TABLE,
    MAR_TABLE,
    get_table_info,
    get_table_properties,
    suggest_data_source,
)

root_agent = pega_when_rule_agent

__all__ = [
    # Models
    "WhenRule",
    "Condition",
    "ConditionGroup",
    "LogicalOperator",
    "Comparator",
    # Agent
    "root_agent",
    "pega_when_rule_agent",
    # HSBC Domain
    "CAR_TABLE",
    "AAR_TABLE",
    "MAR_TABLE",
    "get_table_info",
    "get_table_properties",
    "suggest_data_source",
]
