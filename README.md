# 🏦 Multi-Agent Loan Underwriting System

An intelligent, modular loan underwriting system that automates the loan evaluation process through specialized agents, shared applicant memory, financial computation tools, and rule-based decision-making.

The project demonstrates how a multi-agent architecture can divide a complex loan assessment task into smaller responsibilities, coordinate their outputs, and generate a final underwriting decision.

---

## 🚀 Project Overview

Traditional loan assessment involves several independent checks, including document verification, EMI calculation, affordability analysis, and credit-history evaluation.

This project brings these steps together into a single automated workflow.

Each specialist agent handles a specific underwriting responsibility and stores its findings in a shared applicant record. The underwriting workflow then evaluates the collected information and produces one of three outcomes:

- **SANCTION** – Applicant satisfies the defined underwriting conditions.
- **DECLINE** – Applicant fails the affordability criteria.
- **REFER** – Additional information or manual review is required.

The project includes an interactive Streamlit dashboard for demonstrating the underwriting process.

## ✨ Key Features

- Modular multi-agent architecture.
- Document extraction and validation.
- Automated EMI calculation.
- Loan affordability assessment.
- Credit-history risk evaluation.
- Shared memory for applicant information.
- Rule-based underwriting decisions.
- Execution trace and run logging.
- Interactive Streamlit dashboard.
- Automated test scenarios.

## 🧠 System Architecture

The system consists of five specialized agents:

| Agent | Responsibility |
|---|---|
| Document Agent | Extracts and validates applicant information. |
| EMI Computation Agent | Calculates monthly loan EMI and repayment details. |
| Affordability Agent | Evaluates the applicant's repayment capacity. |
| Credit-History Agent | Retrieves and evaluates credit-history information. |
| Underwriting Manager | Coordinates the underwriting workflow and generates the final decision. |

### Workflow

```text
             Loan Application
                    |
                    v
             Document Agent
                    |
                    v
           Required Field Check
                    |
                    v
             EMI Computation
                    |
                    v
           Affordability Check
                    |
                    v
           Credit-History Check
                    |
                    v
          Underwriting Decision
                    |
          +---------+---------+
          |         |         |
       SANCTION   DECLINE    REFER
```

**Shared Applicant Memory:** Each stage reads or updates the applicant's shared record so that the workflow can use the results of previous assessments.

## 🛠️ Technology Stack

- **Language:** Python
- **Agent Framework:** Microsoft Agent Framework
- **Frontend:** Streamlit
- **Data Processing:** Python
- **Data Storage:** JSON-based synthetic credit records and shared in-memory applicant records
- **Testing:** Python unittest / pytest-compatible test cases
- **Development Environment:** Jupyter Notebook, VS Code

## 📂 Project Structure

```text
MultiAgent_Loan_Underwriting/
│
├── agents/
│   ├── document_agent.py
│   ├── emi_agent.py
│   ├── affordability_agent.py
│   ├── credit_agent.py
│   └── underwriting_manager.py
│
├── data/
│   └── credit_records.json
│
├── app.py
├── config.py
├── tools.py
├── shared_memory.py
├── offline_workflow.py
│
├── test_offline_workflow.py
├── test_document_agent.py
├── test_emi_agent.py
├── test_affordability_agent.py
├── test_credit_agent.py
├── test_underwriting_manager.py
├── test_gemini.py
│
├── Loan_Underwriting_demo.ipynb
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/vaanshgarg/MultiAgent_Loan_UnderWriting.git
```

### 2. Navigate to the project directory

```bash
cd MultiAgent_Loan_UnderWriting
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows (Git Bash):**

```bash
source .venv/Scripts/activate
```

**Windows (Command Prompt):**

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## ▶️ Run the Application

Start the Streamlit dashboard:

```bash
streamlit run app.py
```

The application will open in your browser, where you can enter applicant details and explore the loan underwriting workflow.

## 🧪 Running Tests

Run the main workflow tests:

```bash
python -m pytest test_offline_workflow.py -v
```

Run the complete test suite:

```bash
python -m pytest -v
```

### Test Scenarios

| Scenario | Expected Decision |
|---|---|
| Applicant with valid details and clean credit history | SANCTION |
| Applicant with adverse credit history | REFER |
| Applicant with missing monthly income | REFER |

The workflow stops before EMI computation when required income information is missing.

## 📊 Underwriting Decision Logic

The current offline workflow applies the following rules:

1. Validate the applicant's required information.
2. Refer the application if mandatory information is missing or invalid.
3. Calculate the proposed monthly EMI.
4. Evaluate repayment affordability.
5. Decline applications that fail the affordability threshold.
6. Evaluate the applicant's credit history.
7. Sanction only when affordability passes and no recorded credit-risk flags are found.
8. Refer applications requiring additional review.

**Affordability formula:**

\[
\text{Obligation Ratio} =
\frac{\text{Existing EMI}+\text{Proposed EMI}}
{\text{Monthly Income}}\times100
\]

The default maximum obligation ratio is 40%.

## 🔍 Demo and Execution Trace

The Jupyter notebook `Loan_Underwriting_demo.ipynb` demonstrates the individual agent operations, shared applicant memory, underwriting decisions, and test scenarios.

The application also maintains an execution trace to help understand how the underwriting workflow progresses.

## 🔐 Data and Security

- Credit-history records included in this repository are synthetic demonstration data.
- Do not upload real applicant financial information or personal documents.
- Keep API keys and credentials in environment variables.
- Never commit `.env` files or private credentials.

## ⚠️ Implementation Note

The currently demonstrated Streamlit application uses a deterministic offline Python workflow. The specialist agent modules and Microsoft Agent Framework integration are included in the project, but the dashboard should not be interpreted as using live LLM-based agent delegation.

This is an academic demonstration and is not intended for actual financial lending decisions.

## 🎯 Project Objectives

- Demonstrate a modular multi-agent system.
- Apply financial calculations to loan assessment.
- Implement shared memory between specialized components.
- Automate a structured underwriting workflow.
- Demonstrate decision-making through test scenarios.
- Provide an interactive interface for system evaluation.

## 👨‍💻 Author

**Vansh Garg**  
B.Tech – Computer Science and Engineering (Data Science)  
Lovely Professional University

**GitHub:** [@vaanshgarg](https://github.com/vaanshgarg)

---

⭐ If you find this project interesting, consider giving the repository a star.