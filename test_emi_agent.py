
from shared_memory import shared_memory

from agents.emi_agent import (
    compute_and_store_emi,
    create_repayment_summary,
    create_emi_agent
)


# Create a test applicant
applicant_id = "EMI_TEST_001"

shared_memory.create_applicant(applicant_id)

# Add sample loan details
shared_memory.update_section(
    applicant_id,
    "application",
    {
        "loan_amount": 800000,
        "annual_interest_rate": 10,
        "tenure_months": 60
    }
)

# Test Tool 1
emi_result = compute_and_store_emi(applicant_id)

print("\nMONTHLY EMI RESULT")
print(emi_result)

# Test Tool 2
summary = create_repayment_summary(applicant_id)

print("\nREPAYMENT SUMMARY")
print(summary)

# Verify shared memory
stored_data = shared_memory.get_section(
    applicant_id,
    "emi_analysis"
)

assert stored_data["monthly_emi"] == emi_result["monthly_emi"]
assert stored_data["repayment_summary"]["total_interest"] == summary["total_interest"]

print("\nShared memory verification: PASSED")

# Verify agent construction
agent = create_emi_agent()

print("EMI Agent construction: PASSED")
print("\nALL EMI AGENT TESTS PASSED")
