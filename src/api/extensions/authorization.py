"""Coldline.

===================

File:              src/api/extensions/authorization.py
Component:         API — Authorization constraint (student implementation)
Purpose:           Turn one caller's authorization context into a query-time constraint.
Interacts With:    domain/access.py, the supplied hybrid retrieval adapter
Sprint/Task:       Sprint 2 — Project 2 / Task 2.4
Concepts:          Query-time authorization, declarative predicates
Tools:             Python 3.12

This file is student-editable. Implement `StudentAccessConstraints` and wire it
in `src/api/extensions/wiring.py`.

You return a *declarative* `AccessConstraint`, not SQL. The supplied retrieval
adapter translates it into parameterized predicates inside **both** the dense
and the sparse query, so filtering happens during query execution and an
out-of-scope row is never fetched. That is deliberate: it removes any way to
accidentally build a post-retrieval filter, and it keeps SQL construction in the
protected adapter where it is already parameterized.

Read `src/domain/access.py` first. It defines `AccessConstraint`, and it spells
out the three distinguishable states - unrestricted, restricted, and
deny-everything - because the difference between them is what this Task
assesses.

Implement exactly one of the two supported mechanisms and record which:

- ``tenant_boundary`` restricts tenancy only. The caller reads its own tenancy
  and nothing else, both classification tiers included.
- ``role_classification`` restricts the classification tier only. A
  ``standard`` caller reads ``standard`` content; a ``restricted`` caller reads
  both tiers. Tenancy is not restricted.

Record the one you implemented in ``answers.selected_filter_type``.

Do not implement both, and do not build a multi-attribute policy engine. One
bounded mechanism is the whole Task.

A constraint that denies everything is not a passing answer. It excludes
out-of-scope content trivially and also excludes the caller's own content, so
the permitted-retrieval check fails.
"""

from domain.access import AccessConstraint
from domain.contracts import AuthorizationContext


class StudentAccessConstraints:
    """Return the query-time constraint that applies to one caller.

    Implements `domain.access.AccessConstraintProvider`.
    """

    def constrain(self, authorization: AuthorizationContext) -> AccessConstraint:
        """Return the constraint for one caller."""
        raise NotImplementedError("Task 2.4: implement one bounded authorization constraint")
