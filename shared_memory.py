
"""
Shared Memory Module
Multi-Agent Loan Underwriting System

Provides a central applicant record that all agents
can read and update independently.
"""

from copy import deepcopy
from datetime import datetime, timezone
from threading import RLock
from typing import Any
from uuid import uuid4


class ApplicantMemory:
    """Central shared memory for loan applications."""

    VALID_SECTIONS = {
        "application",
        "document_analysis",
        "emi_analysis",
        "affordability_analysis",
        "credit_analysis",
        "final_decision",
    }

    def __init__(self):
        self._records: dict[str, dict[str, Any]] = {}
        self._lock = RLock()

    def create_applicant(
        self,
        applicant_id: str | None = None,
        application: dict | None = None,
    ) -> str:
        """Create a new, independent applicant record."""

        with self._lock:
            applicant_id = applicant_id or f"APP-{uuid4().hex[:8].upper()}"

            if applicant_id in self._records:
                raise ValueError(
                    f"Applicant {applicant_id} already exists."
                )

            self._records[applicant_id] = {
                "applicant_id": applicant_id,
                "application": deepcopy(application or {}),
                "document_analysis": {},
                "emi_analysis": {},
                "affordability_analysis": {},
                "credit_analysis": {},
                "final_decision": {},
                "execution_trace": [],
                "created_at": self._timestamp(),
                "updated_at": self._timestamp(),
            }

            self.add_trace(
                applicant_id,
                "Shared Memory",
                "Applicant record created",
            )

            return applicant_id

    def get_record(self, applicant_id: str) -> dict:
        """Return a safe copy of the complete applicant record."""

        with self._lock:
            self._ensure_exists(applicant_id)
            return deepcopy(self._records[applicant_id])

    def get_section(self, applicant_id: str, section: str) -> dict:
        """Read a particular section of applicant memory."""

        self._validate_section(section)

        with self._lock:
            self._ensure_exists(applicant_id)
            return deepcopy(self._records[applicant_id][section])

    def update_section(
        self,
        applicant_id: str,
        section: str,
        data: dict,
        agent_name: str = "Unknown Agent",
    ) -> None:
        """Update a section without replacing unrelated sections."""

        self._validate_section(section)

        if not isinstance(data, dict):
            raise TypeError("Section data must be a dictionary.")

        with self._lock:
            self._ensure_exists(applicant_id)

            self._records[applicant_id][section].update(
                deepcopy(data)
            )

            self._records[applicant_id]["updated_at"] = self._timestamp()

            self.add_trace(
                applicant_id,
                agent_name,
                f"Updated {section}",
            )

    def add_trace(
        self,
        applicant_id: str,
        agent_name: str,
        message: str,
    ) -> None:
        """Append an event to the execution history."""

        with self._lock:
            self._ensure_exists(applicant_id)

            self._records[applicant_id]["execution_trace"].append({
                "timestamp": self._timestamp(),
                "agent": agent_name,
                "message": message,
            })

            self._records[applicant_id]["updated_at"] = self._timestamp()

    def list_applicants(self) -> list[str]:
        """Return all stored applicant IDs."""

        with self._lock:
            return list(self._records.keys())

    def _ensure_exists(self, applicant_id: str) -> None:
        if applicant_id not in self._records:
            raise KeyError(
                f"Applicant record not found: {applicant_id}"
            )

    def _validate_section(self, section: str) -> None:
        if section not in self.VALID_SECTIONS:
            raise ValueError(
                f"Invalid section: {section}"
            )

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()


# One shared memory instance for the application.
shared_memory = ApplicantMemory()
