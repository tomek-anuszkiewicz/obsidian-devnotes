---
title: Proxy Metrics and Operational Invariants in AI Systems
tags:
  - ai-decision-systems
  - statistical-bias
  - causal-inference
  - proxy-variables
  - runtime-agents
  - machine-learning
  - algorithmic-fairness
aliases:
  - Statistical Bias, Proxy Variables, and Causal Invariants in AI Systems
  - The House on the Hill Paradox
  - Proxy Variable Trap in Decision Models
  - Ecological Fallacy in AI Systems
  - Statistical Bias vs Causal Invariants
---

# Proxy Metrics and Operational Invariants in AI Systems

Put a decision model in charge of credit underwriting, insurance pricing, fraud investigations, or infrastructure allocation, and it will find patterns in the historical data you give it. A pattern across a group can be useful, but it does not tell you what is true of every person or property in that group. Treating the group average as an individual fact is the **ecological fallacy**.

Removing protected attributes from the input does not remove their influence. A model can recover much of the same information from postal codes, network data, and patterns of behavior. Once the model also decides where to investigate or allocate resources, its decisions shape the data collected next. Retraining on that data can reinforce the original pattern.

The practical rule is simple: **a group-level proxy must not replace or override a fact you can verify directly about the case in front of you** (a principle central to [[Embedding LLMs in Runtime Decision Paths and Operational Telemetry]]). For decisions that matter, the pipeline needs direct checks and a way to examine what would happen under different conditions.

```text
Group-level proxy:       Postal area → Historical flood rate → Risk score
                         A house on higher ground can be rejected.

Operational feedback:    Risk score → Where resources go → What gets recorded
                         The next training set reflects those decisions.

Direct verification:     Water level + foundation elevation → Actual exposure
                         A verified fact takes priority over the area score.
```

---

## Rules for a decision pipeline

1. **Check the individual case.** A model estimates risk from historical correlations, $P(Y|X)$. A house on a 30-meter rocky outcrop can be rejected for flood insurance because the wider postal area has flooded, even when floodwater cannot reach its foundation.
2. **Removing a column does not remove its signal.** A model can infer a protected or biased attribute from browser data, request syntax, purchase intervals, IP subnets, and postal details.
3. **Account for the data your decisions create.** When a model sends staff or audits to one place, the resulting records show what was found there. Feeding those records back into the model can make its original prediction look more accurate than it was.
4. **Go beyond observing correlations.** The decision process needs direct checks, interventions, and tests of alternative conditions, the three levels discussed in Pearl’s framework.
5. **Give verified facts priority.** An area average cannot take precedence over a directly measured physical, financial, or mechanical condition that determines the decision.

---

## When an area score overrules the house on the hill

Credit, fraud, insurance, and cloud capacity systems often produce precise looking scores. The calculation may be sound for the data it was trained on. That does not make the score a measurement of what causes the outcome in one case.

Consider a home in a zone marked as a historical 100-year floodplain. The wider ZIP code has flooded four times in twenty years, so an underwriting model rejects the policy. The home itself sits on a natural 30-meter rocky outcrop. Floodwater cannot reach its foundation. The area's history is real; it is the wrong measurement for this particular house. Flood damage depends on whether water rises above the foundation, not on a postal boundary.

```text
Postal area → Historical floods → Reject the home on the hill
Water crest compared with foundation elevation → No flood exposure → Issue the policy
```

That substitution creates two problems. People are penalized for the demographic, geographic, or network neighborhood around them, even when their own circumstances differ. The business also turns away low-risk, profitable cases while accepting high-risk exceptions hidden inside a group labeled safe (paralleling mechanisms examined in [[AI, Averaged Decisions, and Premature Convergence on Solutions]]). Those are false positives and false negatives from the same shortcut.

---

## 1. Removing sensitive fields still leaves their proxies

A team trying to meet fairness or regulatory requirements may remove race, gender, or age from the training data. The model still has other inputs that correlate with those fields. Neural networks and boosted decision trees can combine those inputs to reconstruct much of the information the team removed.

Device type, browser user-agent, payment timing, mobile carrier, transit route, and a narrowly defined ZIP+4 area can all act as proxies. Suppose a delivery system sees more failed deliveries in one urban sector, or a lender sees more defaults there. If that sector also correlates with a historically marginalized group, the model may penalize that group through its location even without an explicit demographic field.

The loss function rewards the pattern: measured risk falls, and validation against historical data can look good. In operation, the system repeats an existing bias. It may reject a borrower without checking debt service capacity or liquid reserves, or decline a delivery without checking whether the recipient has a secure private gate.

```python
# Removing protected columns still leaves correlated inputs in the model.
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import HistGradientBoostingClassifier

PROTECTED_COLUMNS = ['applicant_race', 'applicant_gender', 'applicant_age']
PROXY_COLUMNS = ['zip_code', 'browser_user_agent', 'device_model', 'isp_provider']
CAUSAL_COLUMNS = ['verified_monthly_cashflow', 'liquid_debt_service_ratio', 'unencumbered_reserves']

# Splits across the proxy columns can recover signals from protected attributes.
feature_preprocessor = ColumnTransformer(
    transformers=[
        ('causal_numeric', StandardScaler(), CAUSAL_COLUMNS),
        ('proxy_categorical', OneHotEncoder(handle_unknown='ignore'), PROXY_COLUMNS)
    ],
    remainder='drop'  # Protected columns are gone; proxies remain.
)

vulnerable_risk_pipeline = Pipeline([
    ('preprocessor', feature_preprocessor),
    ('classifier', HistGradientBoostingClassifier(max_iter=200, max_depth=8))
])
```

---

## 2. A group average is not an individual decision

The **ecological fallacy** is the jump from a group statistic to a claim about one member of that group:

```text
Group statistic:  Cohort A defaults more often than Cohort B.
Individual claim: Person X belongs to Cohort A, so X is a credit risk.
```

In an automated decision path, this happens when the system has detailed information about a group but too little about the individual case. An underwriter might reject an applicant with $250,000 in recurring software engineering income because the neighborhood's median wealth is low. A logistics system might disable same-day delivery to a whole block because package theft is common there, including for customers with secure private drop-boxes. Both systems lose valuable, lower-risk business by treating a neighborhood statistic as the customer's own condition.

Direct verification takes more work than looking up a cohort score. Without it, the model's decision is a form of stereotyping carried out by software.

---

## 3. The model changes the evidence it later learns from

A proxy can do more damage once it controls an operational workflow. Imagine a predictive policing or fraud dispatch system trained on arrest records. Zone A has more recorded arrests, so the model sends 80% of patrols there. More patrols find more minor infractions in Zone A. Zone B is barely checked, so it produces fewer records. On the next training run, the model sees the new arrest counts as confirmation and sends even more patrols to Zone A.

```text
More recorded arrests in Zone A
             ↓
Model predicts more crime there
             ↓
80% of patrols go to Zone A
             ↓
Patrols record more minor infractions there; Zone B gets little coverage
             ↓
New arrest data reinforces the model's prediction
```

The first error is treating arrest records as a direct count of underlying crime. They also reflect where officers were sent. The second is allowing the prediction to decide where new observations will be made. Areas with no patrols may have little recorded activity, which the system reads as little risk. Retraining then feeds the model data shaped by its own previous decisions. Over repeated cycles, attention concentrates on the same places while risks elsewhere become harder to see. The same mechanism can affect staffing, audits, and inspections.

---

## 4. Check the cause and make direct measurements count

The decision pipeline needs a way to distinguish an observed correlation from a condition that actually matters to the outcome. Pearl’s three levels provide a useful way to describe that work:

1. **Association, $P(Y \mid X)$.** What does the applicant's postal code say about historical default rates? This is an observation of a pattern. It is cheap to use and vulnerable to the proxy problems above.
2. **Intervention, $P(Y \mid \operatorname{do}(X))$.** What happens if the system actively verifies the applicant's ability to service debt through open-banking APIs, regardless of location? The pipeline checks a condition instead of accepting a group label.
3. **Counterfactuals, $P(Y_{X=x} \mid X=x', Y=y)$.** Given that a business defaulted, would it have survived a revenue drop if its fixed overhead had been 20% lower? The system examines an alternative set of conditions rather than relying on the historical average of similar businesses.

The rule for a high-stakes pipeline is: **never let a proxy override or substitute for a causal condition that can be measured directly** (see [[Testing in the Model, Agent, LLM Era]] on embedding deterministic invariant checks). In insurance, check LIDAR terrain data, foundation elevation, and drainage rather than only a broad geographic zone. In credit, check current cash flow, liquid reserves, and debt obligations through banking APIs rather than a ZIP code or demographic cluster. The same discipline applies to performance engineering: a general benchmark does not prove that a more complicated implementation will speed up your code. Profile the application under a representative workload on the system that will run it.

The following example makes the priority explicit. A proxy score gives an initial estimate. Verified physical measurements can override it. When those measurements are unavailable, the example falls back to a threshold on the unverified score and says so in the rejection reason.

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class CausalGroundTruth:
    foundation_elevation_meters: float
    historical_max_water_crest_meters: float
    drainage_flow_rate_liters_sec: float

@dataclass(frozen=True)
class UnderwritingDecision:
    approved: bool
    risk_premium: float
    rejection_reason: Optional[str] = None

class UnderwritingPolicyEngine:
    """Let verified flood measurements override the initial proxy score."""

    def __init__(self, statistical_proxy_model, safety_margin_meters: float = 2.0):
        self.proxy_model = statistical_proxy_model
        self.safety_margin_meters = safety_margin_meters

    def evaluate_risk(
        self,
        applicant_payload: dict,
        verified_telemetry: Optional[CausalGroundTruth]
    ) -> UnderwritingDecision:

        # Start with a score based on statistical associations.
        proxy_risk_score = self.proxy_model.predict_proba(applicant_payload)

        if verified_telemetry is not None:
            # Compare the foundation with the recorded maximum water crest.
            elevation_clearance = (
                verified_telemetry.foundation_elevation_meters -
                verified_telemetry.historical_max_water_crest_meters
            )

            if elevation_clearance > self.safety_margin_meters:
                # Verified clearance takes priority over the proxy score.
                return UnderwritingDecision(
                    approved=True,
                    risk_premium=self._calculate_base_rate(verified_telemetry),
                    rejection_reason=None
                )
            elif elevation_clearance <= 0:
                # Reject when the foundation is at or below that water level.
                return UnderwritingDecision(
                    approved=False,
                    risk_premium=0.0,
                    rejection_reason="Causal invariant violated: Foundation below historical crest level."
                )

        # With no decisive measurement, fall back to the unverified score.
        if proxy_risk_score > 0.85:
            return UnderwritingDecision(
                approved=False,
                risk_premium=0.0,
                rejection_reason="High risk threshold exceeded via unverified proxy score."
            )

        return UnderwritingDecision(
            approved=True,
            risk_premium=self._calculate_proxy_rate(proxy_risk_score),
            rejection_reason=None
        )

    def _calculate_base_rate(self, telemetry: CausalGroundTruth) -> float:
        return 100.0 / (telemetry.drainage_flow_rate_liters_sec + 1.0)

    def _calculate_proxy_rate(self, score: float) -> float:
        return score * 500.0
```

---

## Related notes

- **[[Context Attractors and Recency Bias in Long-Horizon Agent Sessions]]** — How an agent can focus on recent conversational cues and lose track of earlier operational constraints.
- **[[AI, Averaged Decisions, and Premature Convergence on Solutions]]** — How optimization can favor average solutions that miss conditions at the edges.
- **[[Embedding LLMs in Runtime Decision Paths and Operational Telemetry]]** — Putting probabilistic models into live workflows and limiting decisions based only on proxies.
- **[[Testing in the Model, Agent, LLM Era]]** — Deterministic checks for drift and proxy failures in production models.
