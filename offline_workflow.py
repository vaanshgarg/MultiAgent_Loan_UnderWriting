
import json

from shared_memory import shared_memory

from tools import (
    read_shared_applicant_record,
    write_final_decision
)

from agents.document_agent import (
    extract_and_store_application,
    validate_stored_application
)

from agents.emi_agent import (
    compute_and_store_emi,
    create_repayment_summary
)

from agents.affordability_agent import (
    calculate_and_store_affordability,
    evaluate_and_store_affordability
)

from agents.credit_agent import (
    lookup_and_store_credit_history,
    evaluate_and_store_credit_risk
)


def run_offline_underwriting(applicant_id, application_text):

    print("\n" + "=" * 55)
    print("OFFLINE LOAN UNDERWRITING")
    print("Applicant:", applicant_id)
    print("=" * 55)

    # STEP 1: Read applicant record
    print("\nSTEP 1: Reading applicant record")

    record_result = read_shared_applicant_record(applicant_id)

    if not record_result["success"]:
        raise ValueError(record_result["error"])

    # STEP 2: Document Agent
    print("\nSTEP 2: Document Agent")

    extraction = extract_and_store_application(
        applicant_id,
        application_text
    )

    print("Extraction:", extraction)

    validation_raw = validate_stored_application(applicant_id)

    if isinstance(validation_raw, str):
        validation_response = json.loads(validation_raw)
    else:
        validation_response = validation_raw

    if not validation_response.get("success", True):
        raise ValueError(
            validation_response.get("error", "Document validation failed.")
        )

    validation = validation_response.get("validation", {})

    print("Validation:", validation)

    # Stop if mandatory information is missing or invalid
    if not validation.get("valid", False):

        if validation.get("income_missing"):
            reason = (
                "Monthly income is missing. Underwriting halted "
                "because affordability cannot be evaluated."
            )
        else:
            reason = (
                "Required application information is missing "
                "or invalid: "
                + ", ".join(validation.get("missing_fields", []))
                + "."
            )

        print("\nAPPLICATION REFERRED")
        print(reason)

        decision_result = write_final_decision(
            applicant_id=applicant_id,
            decision="REFER",
            emi=None,
            affordability_status="NOT_EVALUATED",
            credit_status="NOT_EVALUATED",
            justification=reason
        )

        return {
            "applicant_id": applicant_id,
            "decision": "REFER",
            "reason": reason,
            "final_result": decision_result
        }

    # STEP 3: EMI Agent
    print("\nSTEP 3: EMI Computation Agent")

    emi_result = compute_and_store_emi(applicant_id)

    repayment_summary = create_repayment_summary(applicant_id)

    print("EMI:", emi_result)
    print("Repayment:", repayment_summary)

    # STEP 4: Affordability Agent
    print("\nSTEP 4: Affordability Agent")

    obligation_result = calculate_and_store_affordability(
        applicant_id
    )

    affordability_result = evaluate_and_store_affordability(
        applicant_id
    )

    affordability_status = affordability_result["status"]

    print("Obligation:", obligation_result)
    print("Affordability:", affordability_result)

    # STEP 5: Credit-History Agent
    print("\nSTEP 5: Credit-History Agent")

    credit_history = lookup_and_store_credit_history(
        applicant_id
    )

    credit_result = evaluate_and_store_credit_risk(
        applicant_id
    )

    credit_status = credit_result["status"]

    print("Credit history:", credit_history)
    print("Credit risk:", credit_result)

    # STEP 6: Final decision
    print("\nSTEP 6: Underwriting Manager")

    if affordability_status == "FAIL":

        decision = "DECLINE"

        justification = (
            "The applicant's monthly obligations exceed "
            "the configured affordability threshold of 40%."
        )

    elif (
        affordability_status == "PASS"
        and credit_status == "NO_RECORDED_FLAGS"
        and not credit_result["manual_review_required"]
    ):

        decision = "SANCTION"

        justification = (
            "Application information is complete, EMI is calculated, "
            "monthly obligations are within the configured affordability "
            "limit, and no adverse credit-history indicators were found."
        )

    else:

        decision = "REFER"

        justification = (
            "The application requires manual review because the "
            "credit-history status is "
            + credit_status
            + ". "
            + credit_result["reason"]
        )

    # STEP 7: Save final decision
    print("\nSTEP 7: Saving final decision")

    final_result = write_final_decision(
        applicant_id=applicant_id,
        decision=decision,
        emi=emi_result["monthly_emi"],
        affordability_status=affordability_status,
        credit_status=credit_status,
        justification=justification
    )

    print("\nFINAL DECISION")
    print(final_result)

    return {
        "applicant_id": applicant_id,
        "decision": decision,
        "emi": emi_result["monthly_emi"],
        "affordability_status": affordability_status,
        "credit_status": credit_status,
        "justification": justification,
        "repayment_summary": repayment_summary,
        "final_result": final_result
    }
