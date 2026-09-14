"""Coldline.

===================

File:              src/api/extensions/wiring.py
Component:         API — Student service wiring
Purpose:           Decide which student implementation the application uses.
Interacts With:    api/bootstrap.py, the document repository, domain services
Sprint/Task:       Sprint 2 — Project 2 / Task 2.4
Concepts:          Composition, dependency injection, bounded student surface
Tools:             Python 3.12, PostgreSQL

This file is student-editable, and it is where the application decides which
implementation of a student-owned collaborator it uses.

Task 2.2's service boundary is settled: the reference orchestration service is
now supplied at `src/api/retrieval_orchestration.py`, and this file wires it
without a choice to make.

Task 2.3's data layer is settled: `build_document_repository` now returns the
supplied reference repository.

Task 2.4's factory is `build_access_constraints`. It returns the supplied
unrestricted policy in the starter, which is why retrieval still returns other
tenancies' chunks and the authorization checks fail until you return your own
provider composed with `api.access_policy.ComposedAccessConstraints`.
"""

import asyncpg

from adapters.persistence.document_repository import PostgresDocumentRepository
from api.retrieval_orchestration import RetrievalOrchestrationService
from domain.access import AccessConstraintProvider, UnrestrictedAccessConstraints
from domain.repositories import DocumentRepository
from domain.services import RetrievalOrchestrator
from ports import Retriever


def build_retrieval_orchestrator(
    retriever: Retriever,
    *,
    top_k: int,
    dense_weight: float,
    citation_limit: int,
) -> RetrievalOrchestrator:
    """Return the supplied reference retrieval-orchestration service."""
    return RetrievalOrchestrationService(
        retriever,
        top_k=top_k,
        dense_weight=dense_weight,
        citation_limit=citation_limit,
    )


def build_document_repository(pool: asyncpg.Pool) -> DocumentRepository | None:
    """Return the supplied reference document repository."""
    return PostgresDocumentRepository(pool)


def build_access_constraints() -> AccessConstraintProvider:
    """Return the access-constraint policy the retrieval adapter applies.

    The starter returns the supplied unrestricted policy, which enforces
    nothing: the caller's context is carried through the pipeline and recorded,
    but no content is filtered. Import `api.access_policy.ComposedAccessConstraints`
    and your `api.extensions.authorization.StudentAccessConstraints`. Return
    `ComposedAccessConstraints(StudentAccessConstraints(), selected_filter_type=...)`
    with your explicit choice string, matching `answers.selected_filter_type`.
    The helper supplies the other dimension; never read submission.yaml at runtime.

    The adapter applies whatever this returns inside both query arms, so the
    constraint decides what is *fetched*, not what is discarded afterwards.
    """
    return UnrestrictedAccessConstraints()
