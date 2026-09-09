# Thesis Quality Checklist — "unit tests for English" (Q32)

> This checklist tests the QUALITY OF THE REQUIREMENTS' WRITING, never artifact
> facts. Prohibited: items starting with `Verify`/`Test`/`Confirm`/`Check` +
> behavior. G1 checks artifacts; this checklist checks prose. IDs `CHK###` are
> global and append-only. ≥80% of items carry a traceability ref. Soft cap 40.
> Machine-maintained bidirectionally (agentii.specify generates, agentii.converge
> re-evaluates and reports regressions) — checkboxes can go back to unchecked.

## Requirement Clarity
- [ ] CHK001 每条 `wrong_if` 是否含 metric + threshold + source，而非散文？[Measurability, Spec §1b]

## Requirement Completeness
- [ ] CHK002 universe 的纳入/排除标准是否对每个 ticker 都写明？[Completeness, Spec §2]
- [ ] CHK003 是否定义了空结果场景（筛选后无标的）下的处置？[Coverage, Gap]

## Requirement Consistency
- [ ] CHK004 pillars 之间是否存在互相矛盾的隐含假设？[Conflict]
- [ ] CHK005 各 pillar 的时间视角是否一致（同一 as_of 与同一持有期）？[Consistency]
