# Decision: workflow families with controlled memory/timing variants

Status: implemented specification layer; native expansion not qualified.
Date: 23 October 2026.

User requirement: more coverage with a coherent laboratory benchmark, preserved
scenes, staged long protocols, accurate timing and useful ChemLab assets.
Constraints: preserve frozen v0.1 tasks and data; no LLM/VLM calls; no renewed T6
or cold-restoration investigation; independent grading; useful GPU occupancy.

Alternatives considered:

| Approach | Benefit | Cost / failure mode |
|---|---|---|
| Add independent tasks and asset-specific demonstrations | Quick local progress | Confounds skill, memory and timing; arbitrary count; fragmented interfaces |
| Replace everything with a generic Cartesian task generator | Large formal coverage | Unsupported physical combinations; loses qualified runtime evidence |
| Workflow families, four controlled cells, separate long-protocol and held-out-object axes | Interpretable causal contrasts and explicit reuse | Requires real composition adapters and per-family native qualification |

Choose the third. Reuse `TaskProgram`, `GoalStep`, `TDeadline`, `TDuration` and
`TEvent`. Add a candidate YAML and pure compiler with explicit private/public
output. Keep `ChemRMEnv`, old split files, thresholds, native collection registry
and recorded verdicts intact. No runtime dispatcher is registered for a proposed
template. Long graphs can be serialized but fail closed for unsupported execution.

Evidence for the decision: current seven native tasks, only one isolated memory
task, three qualified timing tasks, a single staged long task, no jointly
controlled M/T family, and no robot-qualified ChemLab held-out object. Existing
semantic grammar remains usable CPU evidence but limits a program to six nodes
and unique primitives; it cannot represent repeated operations in these long
protocols. Use the already-general TaskProgram DAG; do not rewrite or inflate
the legacy grammar.

Acceptance of this change: paired cells retain the same sampled world and goal
graph, public output excludes sampled answers, temporal faults are rejected by
existing checkers, archive corruption is detectable, and no design becomes a
native task by being listed. Native promotion is a later milestone requiring
physical data, public-observation checks and a frozen new evaluation protocol.
