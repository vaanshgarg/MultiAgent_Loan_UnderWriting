cat > README.md <<'EOF'
# Multi-Agent Loan Underwriting System

A Python-based loan underwriting system that uses multiple specialized agents, shared memory, and a Streamlit dashboard to evaluate loan applications.

## Features

- Document Agent: Extracts and validates applicant information.
- EMI Agent: Calculates monthly loan instalments.
- Affordability Agent: Evaluates repayment capacity.
- Credit-History Agent: Checks credit records and risk.
- Underwriting Manager: Coordinates specialist agents.
- Shared Memory: Stores applicant information and agent outputs.
- Streamlit Dashboard: Provides an interactive application interface.
- Offline Workflow: Runs deterministic underwriting decisions without an LLM API.

## Technology Stack

- Python
- Microsoft Agent Framework
- Streamlit
- JSON
- Jupyter Notebook

## Project Structure

```text
MultiAgent_Loan_Underwriting/
├── agents/
│   ├── document_agent.py
│   ├── emi_agent.py
│   ├── affordability_agent.py
│   ├── credit_agent.py
│   └── underwriting_manager.py
├── data/
│   └── credit_records.json
├── app.py
├── config.py
├── offline_workflow.py
├── shared_memory.py
├── tools.py
├── requirements.txt
├── README.md
└── Loan_Underwriting_demo.ipynb