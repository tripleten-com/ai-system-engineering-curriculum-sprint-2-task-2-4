# Task 2.4 contract — one authorization-aware retrieval extension

Implement `StudentAccessConstraints` in `src/api/extensions/authorization.py`, return it from
`build_access_constraints` in `src/api/extensions/wiring.py`, and record which mechanism you
implemented in `submission.yaml`.

## How the extension point works

You return a declarative `AccessConstraint`. You do not write SQL, and you do not filter results.

```text
caller context --> your provider --> AccessConstraint
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

Implement exactly one. The checks verify that the recorded choice is the one the composed policy
implements, and that it restricts *only* its own dimension: a `tenant_boundary` constraint that
also pins the tier fails, and so does the reverse. Do not build a multi-attribute policy engine —
one bounded mechanism is the whole Task.

## Deny-everything is not a pass

`AccessConstraint(tenant_ids=())` excludes every out-of-scope chunk, and also every chunk the
caller is entitled to. The permitted-retrieval check runs an authorized query and requires the
caller's own document back, so a blanket denial fails it. That is the point of the check.

## Where the checks look

| Check | What it verifies |
|---|---|
| composed policy restricts | the supplied unrestricted policy has actually been replaced |
| recorded choice matches | the composed policy implements the mechanism you recorded, and only that dimension |
| permitted retrieval | an authorized query still returns the caller's own document, and the response reports enforcement |
| out-of-scope never fetched | the excluded chunks appear in **no** stage of the response — not in the results, not in the dense or sparse candidate lists, not in what fusion dropped |
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

The `Retriever` port, the retrieval adapter, and `domain/access.py` are protected. You change
behavior behind the published contract, not the contract.
