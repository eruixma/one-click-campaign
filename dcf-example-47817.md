Targeting Criteria (natural language):
This campaign aims to seize this opportunity by identifying these customers just before their bonds mature. it further segments them based on their Risk Profile Questionnaire (RPQ) status. A valid RPO is a regulatory requirement to recommend specific investment products, making it a key differentiator for the marketing approach.

Target Audience Breakdown
Universal Criteria (Applies to ALL targeted customers):
Before being split into groups, all customers selected for this campaign must meet two foundational criteria:
1. They must have a valid investment account with the bank.
2. They must currently hold at least one bond in that account.
Once this base audience is identified, they are segmented into the following three groups for targeted digital marketing.

## Group 1: The "Ready to Reinvest" High-Value Customers
• Description: Valid RPQ & Hold multiple bond
• Criteria:
• They have a valid and up-to-date Risk Profile Questionnaire (RPQ) on file, with a risk tolerance level between 1 and 5.
• They have more than one bond that is scheduled to mature within the next two days.
• Probable Action/Message: This is the most valuable and ready-to-act segment. Since their RPQ is valid, the bank can legally and immediately market specific reinvestment options to them. The message will likely focus on attractive new bond offerings or other investment products to capture the significant funds about to be released from their multiple maturing bonds.

## Group 2: The "Needs Nurturing" Single Bond Holders
• Description: Invalid RPQ & Hold 1 bond
• Criteria:
• Their RPQ is invalid or expired.
• They have exactly one bond maturing within the next two days.
• Probable Action/Message: The bank cannot directly promote investment products to this group. The primary call to action must be to encourage them to renew their RPQ. The messaging would highlight the importance of an up-to-date profile to explore new investment opportunities once their bond proceeds are available.

## Group 3: The "Needs Nurturing" Multiple Bond Holders
• Description: Invalid RPQ & Hold multiple bond
• Criteria:
• Their RPQ is invalid or expired.
• They have more than one bond maturing within the next two days.
• Probable Action/Message: Similar to Group 2, the immediate goal is get them to renew their RPQ. However, the messaging can be framed with more urgency, as a larger sum of capital is about to become available from their multiple maturing bonds. The bank wants to ensure they are ready to discuss reinvestment as soon as their profile is updated.
Exclusion Rule: The "Offer Local" exclusion package is applied to all groups, suggesting that customers marketing offers will be excluded from this campaign.


  Generated When Rule:
Rule 1: OtherStandardExclusion_47817

Rule Name: OtherStandardExclusion_47817
Applies To: Customer Eligibility
Conditions: Multiple rule evaluations (OR conditions)
Expression: If ((Rule IsCustomersHoldingMPF evaluates to true) || {Rule IsMMOCustomers evaluates to true} || {Rule IsValidAccountAcclLevel evaluates to true} || {Rule IsValidAccountCusLevel evaluates to true} || {Rule NonCreditCampaigns evaluates to true} || {Rule IsHKID evaluates to true} || {Rule IsTcTi evaluates to true} || {Rule IsNRCCustomers evaluates to true} || {Rule IsWelfarePayment evaluates to true} || {Rule IsNationalityUSCAKR evaluates to true} || {Rule UnpreferredCustomerList evaluates to true} || {Rule IsFullKYC evaluates to true} || {Rule IsNRCCustomersTaiwan evaluates to true} || {Rule IsHIPB evaluates to true} || {Rule ProductSpecificExclusion_47817 evaluates to true})


Rule 2: StandardExcl_Eligibility

Rule Name: StandardExcl_Eligibility
Applies To: Customer Eligibility
Conditions: Country, Suppression Code, Age, Segment Scheme, Mental Wellbeing Status, GBA Type
Expression: If ((@equalsIgnoreCase(@trim(CUST_CTRY_RELN_CDE10),"USP")) || (@equalsIgnoreCase(@trim(CUST_SUPRS_CDE36),"F_SANT")) || (AGE_NUM < 18) || (@equalsIgnoreCase(@trim(CUST_SUPRS_CDE2),"CPEXCL")) || (@equalsIgnoreCase(@trim(Cust_Seg_Schem_Cde10),"SPA")) || (@Utilities.callWhen(tools,"MentalWellBeing_Ref",ModelDetails)) || (@IsInPageListWhen("SC_GBA_TYPE3",ProductCollateralDetails)) || (AGE_NUM > 65))


Rule 3: ExclNonResidencyInHK

Rule Name: ExclNonResidencyInHK
Applies To: Bond Products
Conditions: Customer Country Code, Static Code Validity, Risk Value, Bond Maturity
Expression: (@notEqualsIgnoreCase(@trim(CUST_CTRY_RELN_CDE8),"NRHK")) && (Rule IsValidStaticCode evaluates to true) && {Rule IsCustRiskValueIn1to5 evaluates to true} && {@greaterThan(BOND_CERT_DEP_MAT_NXT_2_DY_CNT,1)}


Rule 4: IsBondMaturityInLast2Days

Rule Name: IsBondMaturityInLast2Days
Applies To: Bond Products
Conditions: Bond Maturity Days Count, Bond Maturity Date
Expression: {@greaterThan(BOND_CERT_DEP_MAT_NXT_2_DY_CNT,0)} && (@DateTimeDifference(@toDate(BOND_CERT_DEPST_LATE_MTUR_DT),@getCurrent


Rule 5: IsMarketable

Rule Name: IsMarketable
Applies To: Bond Products
Conditions: Suppression Code
Expression: (@notEqualsIgnoreCase(@trim(CUST_SUPRS_CDE18),"NOMK8K"))