## Semantic Comments vs. Syntax Echoes

LLMs parse syntax without help.
They fail when inferring unstated business rules.
Do not explain code mechanics in comments.
Record intent, external constraints, and invariants directly in source files.

```csharp
// BAD: Repeats the code.
// Charge 50% if booking starts in less than 3 days.
if (booking.StartDate < DateTime.UtcNow.AddDays(3)) {
    cancellationFee = booking.TotalPrice * 0.5m;
}

// GOOD: Preserves business constraints.
// Suppliers stop refunds 72 hours before booking starts.
// Do not replace this with the standard hotel cancellation policy.
if (booking.StartDate < DateTime.UtcNow.AddDays(3)) {
    cancellationFee = booking.TotalPrice * 0.5m;
}
```

## Anchor Context Next to Code

Agents fetch files locally during edits.
They miss external tickets, chat threads, and design docs.
Comments placed next to code enter the context window automatically.
Clean method names show what runs, not why contracts exist:

```csharp
ApplyNonRefundableSupplierCancellationFee();
```

Method names omit contract sources, date rules, and vendor quirks.
Use comments to supply these hidden constraints.

Separate system knowledge across distinct tiers:
- Specs: Define product goals.
- ADRs: Track global trade-offs.
- Source comments: Anchor local invariants and exceptions.
- Code: Runs the logic.

Coding models refactor single files without reading parent specs.
Source comments preserve business rules when specs drop out of context.

## Negative Knowledge and Guard Comments

Models often refactor defensive code into generic patterns.
Negative knowledge records forbidden changes and deliberate anomalies.
Use guard comments to stop broken edits:

```csharp
// Do not calculate this from Payment.Amount.
// Legacy bookings store agency margins there.
```

```csharp
// Keep this check.
// Suppliers occasionally send duplicate records with distinct external IDs.
```

```csharp
// Run this before checking availability.
// Sales insists that quoted prices persist when inventory calls fail.
```

Without comments, models apply naive logic:
```text
strange code -> looks redundant -> delete
```

Negative knowledge updates the prompt context:
```text
strange code -> deliberate rule -> keep
```

## Instruct Agents to Preserve Constraints

Direct coding agents to store downstream context when building features.
Use this prompt rule in agent pipelines:

```text
Preserve non-obvious business rules as concise comments next to the code.
```

```text
Spec -> Agent -> Executable Code + Invariant Comments
```

## Invariant Checklist

Write comments to prompt future models.
Audit comments with one test:
What will an agent break if it reads only this file?

Always record:
- Upstream business logic driving the rule.
- Non-obvious domain invariants.
- Deliberate workarounds for external vendor bugs.
- Tempting cleanups that break system guarantees.
