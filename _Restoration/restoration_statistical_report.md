# Statistical Restoration Audit & Quality Gate Report

<style>
table th, table td,
.markdown-rendered table td,
.markdown-rendered table th,
.cm-table-widget td,
.cm-table-widget th {
    vertical-align: top !important;
}
</style>

> [!NOTE]
> Automated statistical sanity check comparing restored notes against their original ground-truth baselines.
> Flags: code block drop, severe shrinkage (<65%), and presence of prohibited degradation markers.

**Total Audited**: 7 | 🟢 **PASS**: 3 | 🟡 **WARN**: 0 | 🔴 **FAIL**: 4

---

| Status | Note Title | Original Words | Restored Words | Code Blocks (Orig -> Rest) | Diagnostic Flags |
| :---: | :--- | :---: | :---: | :---: | :--- |
| 🔴 FAIL | **Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize.md** | 2174 | 3275 | 30 -> 27 | Dropped code: 30 -> 27 blocks |
| 🟢 PASS | **Comments May Become More Valuable in AI-Generated Code.md** | 1249 | 1906 | 12 -> 14 | *(All quality metrics healthy)* |
| 🔴 FAIL | **Designing APIs for LLM-Generated Integration Code.md** | 1447 | 2031 | 25 -> 23 | Dropped code: 25 -> 23 blocks |
| 🟢 PASS | **Designing Software Architecture with LLM Assistance.md** | 3314 | 5175 | 13 -> 15 | *(All quality metrics healthy)* |
| 🟢 PASS | **Developing Features with AI Coding Agents.md** | 487 | 2124 | 2 -> 3 | *(All quality metrics healthy)* |
| 🔴 FAIL | **Hidden Abstractions May Become More Expensive in Agent-Maintained Code.md** | 2509 | 4284 | 71 -> 62 | Dropped code: 71 -> 62 blocks |
| 🔴 FAIL | **LLMs as a Code Review Team.md** | 2562 | 4860 | 41 -> 35 | Dropped code: 41 -> 35 blocks |