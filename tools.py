
"""
Python Tools for Multi-Agent Loan Underwriting System.

These functions will be registered as tools with
Microsoft Agent Framework agents.

Agents:
1. Document Agent
2. EMI Computation Agent
3. Affordability Agent
4. Credit-History Agent
5. Underwriting Manager
"""

import json
import re
from pathlib import Path
from typing import Any

from shared_memory import shared_memory


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
CREDIT_DATABASE = BASE_DIR / "data" / "credit_records.json"


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def _to_number(value: Any, field_name: str) -> float:
    """Convert a value into a valid non-negative number."""

    try:
        number = float(str(value).replace(",", "").replace("₹", "").strip())
    except (ValueError, TypeError):
        raise ValueError(f"{field_name} must be a valid number.")

    if number < 0:
        raise ValueError(f"{field_name} cannot be negative.")

    return number


def _extract_number(text: str, patterns: list[str]):
    """Extract a numeric value using alternative field labels."""

    for pattern in patterns:
        match = re.search(
            pattern + r"\s*[:=-]\s*₹?\s*([\d,]+(?:\.\d+)?)",
            text,
            flags=re.IGNORECASE,
        )

        if match:
            return float(match.group(1).replace(",", ""))

    return None


# ==================================================
# AGENT 1: DOCUMENT AGENT
# ==================================================

def parse_application_fields(application_text: str) -> dict:
    """
    Tool 1: Extract applicant information from text.

    This is a lightweight rule-based parser.
    It does not pretend to perform OCR on images.
    """

    if not isinstance(application_text, str) or not application_text.strip():
        return {"success": False, "error": "Application text is empty."}

    name_match = re.search(
        r"(?:applicant\s+name|name)\s*[:=-]\s*([^\n,]+)",
        application_text,
        flags=re.IGNORECASE,
    )

    extracted = {
        "applicant_name": name_match.group(1).strip() if name_match else None,
        "monthly_income": _extract_number(
            application_text,
            [r"monthly\s+(?:net\s+)?income", r"monthly\s+salary", r"income"],
        ),
        "existing_emi": _extract_number(
            application_text,
            [r"existing\s+emi", r"current\s+emi"],
        ),
        "loan_amount": _extract_number(
            application_text,
            [r"requested\s+loan", r"loan\s+amount"],
        ),
        "annual_interest_rate": _extract_number(
            application_text,
            [r"annual\s+interest\s+rate", r"interest\s+rate"],
        ),
        "tenure_months": _extract_number(
            application_text,
            [r"tenure\s+months", r"loan\s+tenure", r"tenure"],
        ),
    }

    # Save extracted data in shared memory.
    # The application is only partially updated; missing values
    # are not replaced with assumed values.
    return {
        "success": True,
        "extracted_data": extracted,
    }


def validate_required_fields(
    application_data: dict,
) -> dict:
    """
    Tool 2: Validate essential loan application fields.
    Missing income must be reported explicitly.
    """

    required_fields = [
        "applicant_name",
        "monthly_income",
        "existing_emi",
        "loan_amount",
        "annual_interest_rate",
        "tenure_months",
    ]

    missing_fields = [
        field
        for field in required_fields
        if application_data.get(field) is None
        or application_data.get(field) == ""
    ]

    errors = []

    for field in required_fields:
        value = application_data.get(field)

        if value is None or value == "":
            continue

        try:
            if field in required_fields[1:]:
                number = _to_number(value, field)

                if field in {
                    "monthly_income",
                    "loan_amount",
                    "tenure_months",
                } and number <= 0:
                    errors.append(f"{field} must be greater than zero.")

                if field == "tenure_months" and not number.is_integer():
                    errors.append("tenure_months must be a whole number.")

                if field == "annual_interest_rate" and number > 100:
                    errors.append("annual_interest_rate exceeds 100%.")

        except ValueError as exc:
            errors.append(str(exc))

    return {
        "valid": len(missing_fields) == 0 and len(errors) == 0,
        "missing_fields": missing_fields,
        "errors": errors,
        "income_missing": "monthly_income" in missing_fields,
    }


# ==================================================
# AGENT 2: EMI COMPUTATION AGENT
# ==================================================

def calculate_emi(
    principal: float,
    annual_interest_rate: float,
    tenure_months: int,
) -> dict:
    """
    Tool 1: Calculate reducing-balance monthly EMI.

    Formula:
    EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    """

    principal = _to_number(principal, "principal")
    annual_interest_rate = _to_number(
        annual_interest_rate, "annual_interest_rate"
    )

    if principal <= 0:
        raise ValueError("Principal must be greater than zero.")

    if annual_interest_rate > 100:
        raise ValueError("Interest rate cannot exceed 100%.")

    if isinstance(tenure_months, bool):
        raise ValueError("Tenure must be a positive integer.")

    if float(tenure_months) != int(tenure_months):
        raise ValueError("Tenure must be a whole number.")

    tenure_months = int(tenure_months)

    if tenure_months <= 0:
        raise ValueError("Tenure must be greater than zero.")

    monthly_rate = annual_interest_rate / (12 * 100)

    if monthly_rate == 0:
        emi = principal / tenure_months
    else:
        factor = (1 + monthly_rate) ** tenure_months

        emi = (
            principal * monthly_rate * factor
            / (factor - 1)
        )

    return {
        "monthly_emi": round(emi, 2),
        "principal": round(principal, 2),
        "annual_interest_rate": annual_interest_rate,
        "tenure_months": tenure_months,
        "calculation_method": "Reducing Balance",
    }


def generate_repayment_summary(
    principal: float,
    monthly_emi: float,
    tenure_months: int,
) -> dict:
    """
    Tool 2: Calculate total repayment and interest.
    """

    principal = _to_number(principal, "principal")
    monthly_emi = _to_number(monthly_emi, "monthly_emi")

    if isinstance(tenure_months, bool):
        raise ValueError("Tenure must be a positive integer.")

    if float(tenure_months) != int(tenure_months):
        raise ValueError("Tenure must be a whole number.")

    tenure_months = int(tenure_months)

    if principal <= 0 or monthly_emi <= 0 or tenure_months <= 0:
        raise ValueError("All repayment values must be positive.")

    total_repayment = monthly_emi * tenure_months
    total_interest = total_repayment - principal

    return {
        "total_repayment": round(total_repayment, 2),
        "total_interest": round(total_interest, 2),
        "principal": round(principal, 2),
        "tenure_months": tenure_months,
    }


# ==================================================
# AGENT 3: AFFORDABILITY AGENT
# ==================================================

def calculate_obligation_ratio(
    monthly_income: float,
    existing_emi: float,
    proposed_emi: float,
) -> dict:
    """
    Tool 1: Calculate total monthly debt obligation ratio.
    """

    monthly_income = _to_number(monthly_income, "monthly_income")
    existing_emi = _to_number(existing_emi, "existing_emi")
    proposed_emi = _to_number(proposed_emi, "proposed_emi")

    if monthly_income <= 0:
        raise ValueError("Monthly income must be greater than zero.")

    total_obligations = existing_emi + proposed_emi

    ratio = (total_obligations / monthly_income) * 100

    return {
        "monthly_income": round(monthly_income, 2),
        "existing_emi": round(existing_emi, 2),
        "proposed_emi": round(proposed_emi, 2),
        "total_monthly_obligations": round(total_obligations, 2),
        "obligation_ratio": round(ratio, 2),
    }


def check_affordability(
    obligation_ratio: float,
    maximum_ratio: float = 40.0,
) -> dict:
    """
    Tool 2: Apply the configured affordability threshold.
    """

    obligation_ratio = _to_number(
        obligation_ratio, "obligation_ratio"
    )
    maximum_ratio = _to_number(
        maximum_ratio, "maximum_ratio"
    )

    if maximum_ratio <= 0 or maximum_ratio > 100:
        raise ValueError("Maximum ratio must be between 0 and 100.")

    passed = obligation_ratio <= maximum_ratio

    return {
        "affordable": passed,
        "status": "PASS" if passed else "FAIL",
        "obligation_ratio": round(obligation_ratio, 2),
        "maximum_allowed_ratio": maximum_ratio,
        "reason": (
            "Monthly obligations are within the configured limit."
            if passed
            else "Monthly obligations exceed the configured limit."
        ),
    }


# ==================================================
# AGENT 4: CREDIT-HISTORY AGENT
# ==================================================

def lookup_credit_history(applicant_id: str) -> dict:
    """
    Tool 1: Retrieve applicant history from local JSON database.

    A missing record is marked UNKNOWN, not GOOD.
    """

    if not applicant_id or not isinstance(applicant_id, str):
        raise ValueError("A valid applicant ID is required.")

    if not CREDIT_DATABASE.exists():
        return {
            "found": False,
            "status": "UNKNOWN",
            "message": "Credit database does not exist.",
        }

    try:
        with CREDIT_DATABASE.open("r", encoding="utf-8") as file:
            records = json.load(file)
    except (json.JSONDecodeError, OSError) as exc:
        return {
            "found": False,
            "status": "ERROR",
            "message": f"Unable to read credit database: {exc}",
        }

    record = records.get(applicant_id)

    if record is None:
        return {
            "found": False,
            "status": "UNKNOWN",
            "message": "No credit-history record found.",
        }

    return {
        "found": True,
        "status": "FOUND",
        "history": record,
    }


def evaluate_credit_risk(credit_history: dict) -> dict:
    """
    Tool 2: Evaluate local credit-history information.

    This is a prototype review policy, not a real credit score.
    """

    if not credit_history.get("found"):
        return {
            "status": "UNKNOWN",
            "manual_review_required": True,
            "red_flags": [],
            "reason": "Credit history is unavailable or unknown.",
        }

    history = credit_history["history"]

    try:
        defaults = int(history.get("previous_defaults", 0))
        late_payments = int(history.get("late_payments", 0))
        active_overdue = float(history.get("active_overdue", 0))
    except (ValueError, TypeError):
        return {
            "status": "UNKNOWN",
            "manual_review_required": True,
            "red_flags": ["Invalid credit-history data"],
            "reason": "Credit-history values require verification.",
        }

    if defaults < 0 or late_payments < 0 or active_overdue < 0:
        return {
            "status": "UNKNOWN",
            "manual_review_required": True,
            "red_flags": ["Invalid negative credit-history values"],
            "reason": "Credit-history values require verification.",
        }

    red_flags = []

    if defaults > 0:
        red_flags.append("Previous loan defaults")

    if late_payments > 0:
        red_flags.append("Late payment history")

    if active_overdue > 0:
        red_flags.append("Active overdue balance")

    serious_flags = defaults > 0 or active_overdue > 0

    if serious_flags:
        status = "HIGH_RISK"
    elif late_payments > 0:
        status = "REVIEW"
    else:
        status = "NO_RECORDED_FLAGS"

    return {
        "status": status,
        "manual_review_required": status != "NO_RECORDED_FLAGS",
        "red_flags": red_flags,
        "reason": (
            "Adverse credit-history indicators detected."
            if red_flags
            else "No adverse indicators found in available records."
        ),
    }


# ==================================================
# AGENT 5: UNDERWRITING MANAGER
# ==================================================

def read_shared_applicant_record(applicant_id: str) -> dict:
    """
    Manager Tool 1: Read the complete shared applicant record.
    """

    try:
        return {
            "success": True,
            "record": shared_memory.get_record(applicant_id),
        }
    except (KeyError, ValueError) as exc:
        return {
            "success": False,
            "error": str(exc),
        }


def write_final_decision(
    applicant_id: str,
    decision: str,
    emi: float | None,
    affordability_status: str,
    credit_status: str,
    justification: str,
) -> dict:
    """
    Manager Tool 2: Save final underwriting decision.
    """

    allowed_decisions = {"SANCTION", "DECLINE", "REFER"}

    decision = decision.upper().strip()

    if decision not in allowed_decisions:
        raise ValueError("Decision must be SANCTION, DECLINE, or REFER.")

    if not justification or not justification.strip():
        raise ValueError("A justification is required.")

    if decision == "SANCTION":
        if emi is None or affordability_status != "PASS":
            raise ValueError(
                "Cannot sanction without a calculated EMI and passed affordability."
            )

        if credit_status != "NO_RECORDED_FLAGS":
            raise ValueError(
                "Cannot sanction when credit status is not clear."
            )

    result = {
        "decision": decision,
        "monthly_emi": round(float(emi), 2) if emi is not None else None,
        "affordability_status": affordability_status,
        "credit_status": credit_status,
        "justification": justification.strip(),
    }

    shared_memory.update_section(
        applicant_id,
        "final_decision",
        result,
        "Underwriting Manager",
    )

    return {
        "success": True,
        "final_decision": result,
    }
