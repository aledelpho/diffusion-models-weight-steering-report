# Pitfall 88 — drafted 2026-09-29, not yet inserted in `errors_log.md`

## 88 — a claim that something has **not** been done needs a different search from a claim that it has

**What happened.** `parameter_families_first_result.md` §1b ended: *"the two can only be crossed by
a bench that holds one fixed and varies the other, **which no bench in this project has yet
done**."* Committed as `1bae474`. Two hours later, asked whether `F_wo` could be split by block, I
looked in `presets/` and found `Arthemy_QKVO_wo_b1_{pos,neg}` and `Arthemy_QKVO_wo_b6_{pos,neg}` —
exactly `Family_wo_d+0.100` restricted to one group, same delta, already rendered in
`benchmark_qkvo_atlas`, 24 cells per condition. The cross existed, and the split had already shown
the two ends of the stack behaving differently.

**Why the existing rule did not catch it.** Pitfall 87, written the day before, says: before
reporting a finding, grep `docs/` and `notebook/` in **both languages** and record what the search
returned. I did that — for the *finding*. The sentence that was wrong was not a finding but a
**negative claim about the corpus**, and a negative claim about the corpus is not falsified by
documents. It is falsified by **artefacts**: presets, plans, render folders. Those I did not search.

**The rule.** Before writing that something has not been done, has never been tried, or does not
exist:

1. grep `presets/` for the parameter or condition by name;
2. grep `data/*plan*.csv` and `data/*.csv` for the condition, and list the render folders;
3. only then `docs/` and `notebook/`, in both languages;
4. record in the document what each of the three searches returned, including "nothing".

A document may fail to mention an experiment that was run. A preset file cannot fail to exist.
**The artefacts are the stronger evidence, and they are the ones I skipped.**

**Cost of this instance.** Low — it was caught within hours, by Alessandro's question rather than by
me, and the correction is in the same document. But it is the third time in three days that a
statement was published which the repository itself contradicted (see 87, and the `normscales`
retraction before it), and the first two were also caught by him asking.
