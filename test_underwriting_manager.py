
from shared_memory import shared_memory

from tools import (
    read_shared_applicant_record,
    write_final_decision
)

from agents.underwriting_manager import (
    create_underwriting_manager
)


# Test applicant
applicant_id = "MANAGER_TEST_001"

# Create applicant
shared_memory.create_applicant(applicant_id)


# TEST 1: Manager read tool
read_result = read_shared_applicant_record(applicant_id)

print("\nMANAGER READ TOOL")
print(read_result)

assert read_result["success"] is True


# TEST 2: Manager write tool
write_result = write_final_decision(
    applicant_id=applicant_id,
    decision="REFER",
    emi=None,
    affordability_status="NOT_EVALUATED",
    credit_status="NOT_EVALUATED",
    justification=(
        "Manager tool test: application requires "
        "further review."
    )
)

print("\nMANAGER WRITE TOOL")
print(write_result)

assert write_result["success"] is True
assert write_result["final_decision"]["decision"] == "REFER"


# TEST 3: Verify shared memory
stored_decision = shared_memory.get_section(
    applicant_id,
    "final_decision"
)

print("\nSTORED FINAL DECISION")
print(stored_decision)

assert stored_decision["decision"] == "REFER"

print("\nShared memory verification: PASSED")


# TEST 4: Construct complete manager and worker architecture
manager = create_underwriting_manager()

assert manager is not None

print("\nUnderwriting Manager construction: PASSED")

print("\nALL UNDERWRITING MANAGER CONSTRUCTION TESTS PASSED")
