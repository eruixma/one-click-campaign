"""Tests for HSBC domain module."""

import pytest
from pega_agent.hsbc_domain import (
    CAR_TABLE,
    AAR_TABLE,
    MAR_TABLE,
    DataGranularity,
    get_table_info,
    get_table_properties,
    suggest_data_source,
)


class TestAnalyticalRecordTables:
    def test_car_table_config(self):
        assert CAR_TABLE.name == "CAR"
        assert CAR_TABLE.full_name == "Customer Analytical Record"
        assert CAR_TABLE.granularity == DataGranularity.CUSTOMER
        assert CAR_TABLE.pega_class == "HSBC-Data-CAR"
        assert "PseudoCustomerID" in CAR_TABLE.keys
        assert CAR_TABLE.technical_criteria is not None

    def test_aar_table_config(self):
        assert AAR_TABLE.name == "AAR"
        assert AAR_TABLE.full_name == "Account Analytical Record"
        assert AAR_TABLE.granularity == DataGranularity.CUSTOMER_ACCOUNT
        assert AAR_TABLE.pega_class == "HSBC-Data-AAR"
        assert "PseudoCustomerID" in AAR_TABLE.keys
        assert "PseudoAccountID" in AAR_TABLE.keys
        assert "RoleType" in AAR_TABLE.keys

    def test_mar_table_config(self):
        assert MAR_TABLE.name == "MAR"
        assert MAR_TABLE.full_name == "Modeling Analytical Record"
        assert MAR_TABLE.granularity == DataGranularity.CUSTOMER
        assert MAR_TABLE.pega_class == "HSBC-Data-MAR"
        assert "PseudoCustomerID" in MAR_TABLE.keys


class TestGetTableInfo:
    def test_returns_all_tables(self):
        result = get_table_info()
        assert "tables" in result
        assert len(result["tables"]) == 3

        table_names = [t["name"] for t in result["tables"]]
        assert "CAR" in table_names
        assert "AAR" in table_names
        assert "MAR" in table_names

    def test_table_info_structure(self):
        result = get_table_info()
        for table in result["tables"]:
            assert "name" in table
            assert "full_name" in table
            assert "scope" in table
            assert "granularity" in table
            assert "keys" in table
            assert "pega_class" in table


class TestGetTableProperties:
    def test_car_properties(self):
        result = get_table_properties("CAR")
        assert result["table"] == "CAR"
        assert "properties" in result
        assert len(result["properties"]) > 10

        prop_names = [p["name"] for p in result["properties"]]
        assert ".CustomerAge" in prop_names
        assert ".CustomerSegment" in prop_names
        assert ".TotalRelationshipBalance" in prop_names

    def test_aar_properties(self):
        result = get_table_properties("AAR")
        assert result["table"] == "AAR"

        prop_names = [p["name"] for p in result["properties"]]
        assert ".AccountType" in prop_names
        assert ".CurrentBalance" in prop_names
        assert ".CreditUtilization" in prop_names

    def test_mar_properties(self):
        result = get_table_properties("MAR")
        assert result["table"] == "MAR"

        prop_names = [p["name"] for p in result["properties"]]
        assert ".PropensityCreditCard" in prop_names
        assert ".ChurnProbability" in prop_names
        assert ".NBARecommendation" in prop_names

    def test_case_insensitive(self):
        result_lower = get_table_properties("car")
        result_upper = get_table_properties("CAR")
        assert result_lower["table"] == result_upper["table"]

    def test_invalid_table(self):
        result = get_table_properties("INVALID")
        assert "error" in result


class TestSuggestDataSource:
    def test_customer_context_suggests_car(self):
        result = suggest_data_source("customer age and segment")
        assert result["recommendation"]["table"] == "CAR"

    def test_account_context_suggests_aar(self):
        result = suggest_data_source("account balance and transactions")
        assert any(s["table"] == "AAR" for s in result["suggestions"])

    def test_propensity_context_suggests_mar(self):
        result = suggest_data_source("propensity score for credit card")
        assert any(s["table"] == "MAR" for s in result["suggestions"])

    def test_churn_context_suggests_mar(self):
        result = suggest_data_source("churn risk and retention")
        assert any(s["table"] == "MAR" for s in result["suggestions"])

    def test_returns_recommendation(self):
        result = suggest_data_source("customer tenure")
        assert "recommendation" in result
        assert result["recommendation"] is not None
        assert "table" in result["recommendation"]
        assert "reason" in result["recommendation"]
        assert "class" in result["recommendation"]
