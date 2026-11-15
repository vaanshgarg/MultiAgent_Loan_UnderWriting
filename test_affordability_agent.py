
from shared_memory import shared_memory

from agents.affordability_agent import (
    calculate_and_store_affordability,
    evaluate_and_store_affordability,
    create_affordability_agent
)

applicant_id = "AFFORDABILITY_TEST_001"

# Create applicant
shared_memory.create_applicant(applicant_id)

# Add sample application details
shared_memory.update_section(
    applicant_id,
    "application",
    {
        "monthly_income": 65000,
        "existing_emi": 5000
    }
)

# Add proposed EMI from EMI Agent
shared_memory.update_section(
    applicant_id,
    "emi_analysis",
    {
        "monthly_emi": 16997.64
    }
)

# Test Tool 1
ratio_result = calculate_and_store_affordability(
    applicant_id
)

print("\nOBLIGATION RATIO RESULT")
print(ratio_result)

# Test Tool 2
affordability_result = evaluate_and_store_affordability(
    applicant_id
)

print("\nAFFORDABILITY EVALUATION")
print(affordability_result)

# Verify shared memory
stored_data = shared_memory.get_section(
    applicant_id,
    "affordability_analysis"
)

assert stored_data is not None
assert stored_data["obligation_details"]["obligation_ratio"] == 33.84
assert "evaluation" in stored_data

print("\nShared memory verification: PASSED")

# Verify agent construction
agent = create_affordability_agent()

print("Affordability Agent construction: PASSED")
print("\nALL AFFORDABILITY AGENT TESTS PASSED")
