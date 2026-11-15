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

## 🛠️ Technology