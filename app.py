
import streamlit as st
import uuid
import json

from shared_memory import shared_memory
from offline_workflow import run_offline_underwriting


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Loan Underwriting System",
    page_icon="🏦",
    layout="wide"
)

# ---------------- CUSTOM HEADER ----------------

st.title("🏦 Multi-Agent Loan Underwriting System")

st.markdown(
    """
    An AI-assisted loan underwriting demonstration
    powered by specialist agents and shared applicant memory.
    """
)

st.divider()

# ---------------- SIDEBAR ----------------

st.sidebar.title("System Information")
st.sidebar.success("Python workflow connected")

st.sidebar.markdown("""
**Agents in this project**

1. Document Agent
2. EMI Computation Agent
3. Affordability Agent
4. Credit-History Agent
5. Underwriting Manager
""")

st.sidebar.info(
    "This interface currently executes the deterministic "
    "Python workflow. It does not demonstrate live LLM delegation."
)

# ---------------- APPLICATION FORM ----------------

st.subheader("📋 Applicant Information")

with st.form("loan_application"):

    col1, col2 = st.columns(2)

    with col1:
        applicant_name = st.text_input(
            "Applicant Name",
            value="Demo Applicant"
        )

        missing_income = st.checkbox(
            "Monthly income not provided"
        )

        monthly_income = st.number_input(
            "Monthly Net Income (₹)",
            min_value=0.0,
            value=65000.0,
            step=1000.0,
            disabled=missing_income
        )

        existing_emi = st.number_input(
            "Existing Monthly EMI (₹)",
            min_value=0.0,
            value=5000.0,
            step=500.0
        )

    with col2:
        loan_amount = st.number_input(
            "Requested Loan Amount (₹)",
            min_value=1000.0,
            value=800000.0,
            step=10000.0
        )

        interest_rate = st.number_input(
            "Annual Interest Rate (%)",
            min_value=0.1,
            value=12.0,
            step=0.5
        )

        tenure_months = st.number_input(
            "Loan Tenure (Months)",
            min_value=1,
            max_value=360,
            value=60,
            step=1
        )

    submitted = st.form_submit_button(
        "🚀 Run Loan Underwriting",
        use_container_width=True
    )


# ---------------- EXECUTION ----------------

if submitted:

    if not applicant_name.strip():
        st.error("Please enter the applicant's name.")

    else:
        applicant_id = "APP-" + uuid.uuid4().hex[:8].upper()

        income_text = (
            ""
            if missing_income
            else str(monthly_income)
        )

        application_text = f"""
Applicant Name: {applicant_name}
Monthly Income: {income_text}
Existing EMI: {existing_emi}
Requested Loan: {loan_amount}
Annual Interest Rate: {interest_rate}
Tenure Months: {tenure_months}
"""

        try:
            with st.spinner(
                "Underwriting system is processing the application..."
            ):

                # Create shared applicant record
                shared_memory.create_applicant(applicant_id)

                # Execute existing workflow
                result = run_offline_underwriting(
                    applicant_id,
                    application_text
                )

                # Retrieve shared memory
                record = shared_memory.get_record(applicant_id)

            st.session_state["result"] = result
            st.session_state["record"] = record
            st.session_state["applicant_id"] = applicant_id

        except Exception as error:
            st.error(f"Workflow execution failed: {error}")


# ---------------- DISPLAY RESULTS ----------------

if "result" in st.session_state:

    result = st.session_state["result"]
    record = st.session_state["record"]
    applicant_id = st.session_state["applicant_id"]

    final_data = (
        result.get("final_result", {})
        .get("final_decision", {})
    )

    decision = result.get(
        "decision",
        final_data.get("decision", "NOT AVAILABLE")
    )

    st.divider()
    st.header("📊 Underwriting Results")

    st.write(f"**Applicant ID:** {applicant_id}")

    if decision == "SANCTION":
        st.success("✅ LOAN SANCTIONED")

    elif decision == "DECLINE":
        st.error("❌ LOAN DECLINED")

    elif decision == "REFER":
        st.warning("⚠️ APPLICATION REFERRED FOR REVIEW")

    else:
        st.info(f"Decision: {decision}")

    # Metrics
    monthly_emi = final_data.get(
        "monthly_emi",
        result.get("emi")
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Monthly EMI",
            f"₹{monthly_emi:,.2f}"
            if isinstance(monthly_emi, (int, float))
            else "Not calculated"
        )

    with col2:
        st.metric(
            "Affordability",
            result.get(
                "affordability_status",
                final_data.get("affordability_status", "N/A")
            )
        )

    with col3:
        st.metric(
            "Credit Status",
            result.get(
                "credit_status",
                final_data.get("credit_status", "N/A")
            )
        )

    # Justification
    st.subheader("📝 Decision Justification")

    justification = result.get(
        "justification",
        final_data.get(
            "justification",
            result.get("reason", "No justification available.")
        )
    )

    st.info(justification)

    # Repayment details
    with st.expander("💰 Repayment Summary"):
        st.json(result.get("repayment_summary", {}))

    # Agent outputs
    st.divider()
    st.header("🤖 Agent Execution Details")

    sections = [
        ("Document Agent", "document_analysis"),
        ("EMI Computation Agent", "emi_analysis"),
        ("Affordability Agent", "affordability_analysis"),
        ("Credit-History Agent", "credit_analysis"),
        ("Underwriting Manager", "final_decision")
    ]

    for agent_name, section_key in sections:

        with st.expander(agent_name):

            section_data = record.get(section_key, {})

            if section_data:
                st.json(section_data)
            else:
                st.write("No output recorded for this agent.")

    # Execution trace
    st.divider()
    st.subheader("🔍 Execution Trace")

    trace = record.get("execution_trace", [])

    if trace:
        for index, item in enumerate(trace, start=1):
            st.write(f"**Step {index}**")
            st.json(item)
    else:
        st.write("No execution trace available.")

    # Complete shared memory
    with st.expander("🧠 Complete Shared Applicant Memory"):
        st.json(record)

    # Raw workflow output
    with st.expander("Raw Workflow Result"):
        st.json(result)

st.divider()

st.caption(
    "Multi-Agent Loan Underwriting System | "
    "Academic project demonstration"
)
