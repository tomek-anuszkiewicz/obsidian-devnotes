---
name: incremental-vault-maintenance
description: Review vault note structure and links together, using a shared Git commit checkpoint to process every committed note change since the last completed pass. Use for requested vault maintenance runs, not ordinary note edits.
---

# Incremental Vault Maintenance

Use one checkpoint for the combined structure and linking pass. The checkpoint is a tracked file at `.agents/state/vault-maintenance-checkpoint.txt` containing only the full commit ID last covered by a completed pass. Read its committed version from `HEAD`, not an uncommitted working-tree copy. Do not keep a per-file review register.

## Select the scope

- If the checkpoint file does not exist in `HEAD`, perform a **full first pass** over every Markdown note in the six numbered content folders. Do not initialize the checkpoint to the current `HEAD` or claim that existing notes have already been reviewed.
- Otherwise, verify that the stored ID names a commit in the current history and is an ancestor of `HEAD`. Include every note added, modified, renamed, or deleted between that commit and the starting `HEAD`. Ignore changes to skills, scripts, and the checkpoint file when selecting notes. If the stored commit is invalid or the history has diverged, stop and explain the problem rather than silently resetting the checkpoint.
- The changed notes are the review scope, not a restriction on reading context. Search other notes when needed to judge a merge, identify a meaningful link, or repair links to a renamed or deleted note. Do not turn an incremental pass into an unrequested full-vault review.
- Preserve pre-existing working-tree changes. If an uncommitted edit overlaps a note that the pass must change, resolve that scope before editing it; never overwrite or reset the user's work.

## Review, decide, and link

1. Apply `vault-note-structure-review` to every existing note in scope. For deleted notes, inspect the former title and incoming links rather than trying to review a missing file. Collect concrete split, merge, and deliberate-copy recommendations. A recommendation alone does not authorize restructuring.
2. Present the structural proposals together. Let the user accept, reject, or defer each one. Implement only accepted proposals. A rejected proposal counts as reviewed for this pass; a deferred or unanswered proposal leaves the pass incomplete.
3. Apply `vault-linking` after any accepted restructuring. Improve links in the changed and newly created notes automatically, and repair affected incoming links when a note was renamed, split, merged, or deleted. Verify targets and add links only where they help the reader; do not force reciprocal links or replace necessary local explanation with a link.
4. Validate the edited notes and review the diff. Report what was reviewed, what changed, what was rejected, and any unresolved work. Do not advance the checkpoint if either review, a required decision, or validation remains incomplete.

## Persist completed progress

The checkpoint must be available in the repository on GitHub, so update the tracked file only after the entire pass succeeds. Do not create a commit or push unless the user has explicitly authorized those actions; if authorization is still needed, present the completed changes first and request it as the final step.

When commit and push are authorized, commit only the intended note changes first. Recheck that no additional unreviewed note commits entered the range. Write the resulting reviewed `HEAD` commit ID to the checkpoint file, commit that file separately, then push. If the pass made no note changes, store the reviewed starting `HEAD` and commit only the checkpoint file. Never store the ID of the checkpoint commit inside itself. If publishing fails, report that the GitHub checkpoint did not advance.

Do not mark an incomplete pass complete. On the next run, start again from the checkpoint that remains in the tracked file.
