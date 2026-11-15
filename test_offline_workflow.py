
from shared_memory import shared_memory

from offline_workflow import run_offline_underwriting


def run_test(applicant_id, application_text, expected_decision):

    shared_memory.create_applicant(applicant_id)

    result = run_offline_underwriting(
        applicant_id,
        application_text
    )

    print("\nTEST RESULT:", result["decision"])

    assert result["decision"] == expected_decision

    record = shared_memory.get_record(applicant_id)

    assert record["final_decision"]["decision"] == expected_decision

    if expected_decision == "REFER" and "Monthly income is missing" in result.get("reason", ""):
        assert not record["emi_analysis"].get("monthly_emi")

    print("TEST PASSED:", applicant_id)

    return result


# SCENARIO 1: Complete application with clean credit history
print("\n\nSCENARIO 1: CLEAN APPLICATION")

scenario_1 = run_test(
    "APP001",
    """
    Applicant Name: Rahul Sharma
    Monthly Income: 65000
    Existing EMI: 5000
    Requested Loan: 800000
    Annual Interest Rate: 10
    Tenure Months: 60
    """,
    "SANCTION"
)


# SCENARIO 2: Applicant with adverse credit history
print("\n\nSCENARIO 2: ADVERSE CREDIT HISTORY")

scenario_2 = run_test(
    "APP002",
    """
    Applicant Name: Amit Kumar
    Monthly Income: 65000
    Existing EMI: 5000
    Requested Loan: 800000
    Annual Interest Rate: 10
    Tenure Months: 60
    """,
    "REFER"
)


# SCENARIO 3: Missing monthly income
print("\n\nSCENARIO 3: MISSING MONTHLY INCOME")

scenario_3 = run_test(
    "APP003",
    """
    Applicant Name: Neha Sharma
    Existing EMI: 5000
    Requested Loan: 800000
    Annual Interest Rate: 10
    Tenure Months: 60
    """,
    "REFER"
)


# FINAL SUMMARY
print("\n" + "=" * 55)
print("OFFLINE UNDERWRITING TEST SUMMARY")
print("=" * 55)

print("Scenario 1:", scenario_1["decision"])
print("Scenario 2:", scenario_2["decision"])
print("Scenario 3:", scenario_3["decision"])

print("\nALL THREE OFFLINE SCENARIOS PASSED!")
