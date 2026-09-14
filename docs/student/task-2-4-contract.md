# Task 2.4 contract — one authorization-aware retrieval extension

Implement `StudentAccessConstraints` in `src/api/extensions/authorization.py`, compose it with the protected helper from
`build_access_constraints` in `src/api/extensions/wiring.py`, and record which mechanism you
implemented in `submission.yaml`.

## How the extension point works

You return a declarative `AccessConstraint`. You do not write SQL, and you do not filter results.

```text
caller context --> your provider (one dimension)
                         + supplied complementary dimension
                                          |
                                   AccessConstraint
                                          |
                    the supplied adapter turns it into parameterized
                    predicates INSIDE the dense query AND the sparse query
                                          |
                      out-of-scope rows are never fetched at all
```

That shape is deliberate. Filtering at query time is the requirement, and the only way to satisfy
it here is to constrain the query — there is no place in your surface to drop rows afterwards. It
also keeps SQL construction inside the protected adapter, where it is already parameterized.

Read `src/domain/access.py` first. It defines `AccessConstraint` and names its three
distinguishable states, which is exactly what this Task turns on:

| Value | Meaning |
|---|---|
| `AccessConstraint()` | no restriction — every stored chunk is readable |
| `AccessConstraint(tenant_ids=("tenant-a",))` | only that tenancy is readable |
| `AccessConstraint(tenant_ids=())` | nothing is readable |

## Your two choices

| Choice | Recorded value | What the constraint must restrict |
|---|---|---|
| Tenant boundary | `tenant_boundary` | tenancy only — the caller reads its own tenancy, both tiers |
| Role classification | `role_classification` | classification tier only — a `standard` caller reads `standard` content; a `restricted` caller reads both tiers |

Implement exactly one in `StudentAccessConstraints`. These checks inspect your provider
separately: it must restrict only its selected dimension. A tenant provider that also restricts
tiers fails this boundary, and so does a role provider that also restricts tenants.

In `src/api/extensions/wiring.py`, import `ComposedAccessConstraints` from `api.access_policy`.
Return `ComposedAccessConstraints(StudentAccessConstraints(), selected_filter_type=...)` from
`build_access_constraints`, passing either `"tenant_boundary"` or `"role_classification"`
explicitly. Record the same value in `answers.selected_filter_type`; the application must never
read the answer sheet at runtime.

The protected helper supplies the complementary dimension. The completed application always
requires both the caller's tenant and a permitted classification tier. It preserves your selected
dimension unchanged, so it cannot repair an incorrect or missing student filter. `None` means
unrestricted; `()` means deny-all, including during composition. An invalid choice, missing
composition, mismatched answer, or blanket denial fails verification.

## Deny-everything is not a pass

`AccessConstraint(tenant_ids=())` excludes every out-of-scope chunk, and also every chunk the
caller is entitled to. The permitted-retrieval check runs an authorized query and requires the
caller's own document back, so a blanket denial fails it. That is the point of the check.

## Where the checks look

| Check | What it verifies |
|---|---|
| composed policy restricts | the protected helper composes both dimensions for multiple tenants and clearances |
| recorded choice matches | your provider implements exactly its selected dimension and the explicit wiring choice matches your answer |
| permitted retrieval | an authorized query still returns the caller's own document, and the response reports enforcement |
| out-of-scope never fetched | foreign-tenant and unauthorized restricted chunks appear in **no** stage of the response — not in the results, not in the dense or sparse candidate lists, not in what fusion dropped |
| cleared caller | an authorized caller still reaches the content the other caller could not, so exclusion depends on the caller rather than being a blanket removal |
| published contract | `Retriever` still exposes exactly `search_hybrid(request)` |

The out-of-scope check reads the stage evidence, not only the final results, because a filter
applied after retrieval would leave the excluded identifiers visible in the candidate lists. Run
the checks with `poe authorization`, or the whole public gate with `poe verify`.

## Permitted paths

- `src/api/extensions/authorization.py`
- `src/api/extensions/wiring.py`
- anything else you add under `src/api/extensions/`
- anything you add under `tests/student/`
- `submission.yaml`

The `Retriever` port, the retrieval adapter, `domain/access.py`, and `api/access_policy.py` are protected. You change
behavior behind the published contract, not the contract.
