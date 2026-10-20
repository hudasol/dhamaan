# Research question

Status: draft for the author to confirm. Written before any recorded data was replayed and before any row of the human check was read. Later changes are made by dated amendment at the foot of this page, not by editing the text above it.

## The question

> Where no instrument fixes the conditions a service robot must be shown safe under, do a developer written synthetic fault generator and recorded real GNSS interference give the same pass or fail verdict for the same integrity monitor and the same thresholds, and can published simulation credibility conditions predict where the two disagree?

In plain words: a team that builds a safety monitor also builds the simulation that tests it. If the regulation does not say which conditions count, the team's own simulation becomes the evidence. We ask whether that evidence agrees with what happens on recorded real data, and whether the credibility rules that already exist in other fields would have warned us.

## Why this question

It follows from what the study found, not from a wish for a topic.

1. **Silence.** No instrument retrieved asks a developer to test against Gulf heat, dust, sun glare or GNSS interference (`docs/REPORT.md`, finding 4). Test methods exist; the severity that applies at a site is left to the developer.
2. **Simulation is accepted under conditions, with no quantity.** SORA guidance, UL 4600, NASA STD 7009 and others allow simulation if its use is justified, and none gives a rule for how much of a claim it may carry (rows D38, B07, D27, D28).
3. **The study's own weakness is the object.** Our simulations were written by the authors of the monitors they test, with assumed thresholds, and ten acceptance criteria failed across two rounds. Instead of hiding that circularity we test it: we replace the synthetic arm with recorded data and compare verdicts.
4. **The region matters.** Trade press reports widespread GNSS jamming and spoofing in the Gulf in 2026 (source S40 in `data/related_work.csv`). A detector tuned on tidy synthetic faults may behave differently where interference is real.

## What is already known, and what is left

A search of the literature (`docs/RELATED_WORK.md`, `data/related_work.csv`) found that the general framework question, how much credit simulation can carry and what must be shown about the simulator, is already treated in recent work: risk based credibility frameworks (S03, S05), an admissibility ladder for simulators (S06), the NASA credibility scale (S01) and independence of verification (S12). We therefore do not propose a new credibility framework. We adopt external conditions and encode them. Two pieces remain open in what we read:

- a comparison of verdicts on the same monitor between synthetic and recorded interference, for a robot, with thresholds fixed in advance;
- an audit of what the standards leave to the developer for the conditions that matter in the Gulf.

The search read abstracts and page summaries, and paywalled standards could not be read. Absence from our results is not absence from the literature.

## Sub questions and hypotheses

| Id | Hypothesis | Data and test | What would falsify it |
|---|---|---|---|
| H1 | Among retrieved instruments that ask for environmental or interference evidence, test methods are fixed more often than severities, and none fixes severities for Gulf heat, dust, sun or GNSS interference. | Candidate rows from the evidence table (`data/silence_audit/`), coded by two coders with a written codebook; agreement reported. Result limited to retrieved text. | Any retrieved instrument that fixes a severity applicable to the Gulf. |
| H2 | Four published conditions can be checked by machine on an assurance case without judgement: stated context of use, validation against physical data, reported uncertainty or sensitivity, and independence of the verifier from the developer. | Encode the conditions in the case checker; a second coder classifies every evidence item; agreement reported. | Agreement below the preregistered level, meaning the conditions need judgement. |
| H3 | At least one acceptance verdict for the GNSS monitor differs between the synthetic arm and the recorded arm. | Round 3: same monitor, same thresholds, recorded logs with known intervals against the synthetic generator. | No verdict differs; the synthetic arm is then adequate for this monitor. |
| H4 | On recorded data the monitor detects later and raises more false alarms, because recorded errors are correlated in time and heavy tailed. | Detection delay and false alarm rate by arm. | Equal or opposite direction. |
| H5 | A generator recalibrated on a training set of recordings reproduces the verdicts on held out recordings; the original generator does not. | Split recordings before looking at results; calibrate on one part, score on the other. | The recalibrated generator still disagrees on held out data: synthetic faults cannot stand in for this claim. |

Negative results answer the question too. If H3 fails, simulation was adequate here and the case checker may credit it; if H5 fails, it should not.

## How the repository answers it

| Part | Role |
|---|---|
| Evidence table | Source of the silence audit (H1) and of the credibility conditions we adopt (H2). |
| Assurance case | Holds claim G6 (GNSS fault handling). A credit ledger states, per evidence item, which conditions it meets and the ceiling on the claim it can support. |
| Simulation rounds 1 and 2 | The synthetic arm for H3 to H5. Dust, glare and heat stay as demonstrations with no recorded arm and receive the lowest credit. |
| Round 3 | Recorded arm, informativeness audit of predictions, sensitivity analysis (see `docs/PREREG_R3_DRAFT.md`). |
| Human check | Measures how far the evidence table can be relied on for the rows H1 and H2 use (`data/human_check/`). |

## Scope and what is not claimed

- One monitor, one hazard with a recorded arm (GNSS). Glare, dust and heat have no recorded arm in this study.
- Public recordings may come from outside the Gulf. A Gulf claim needs Gulf recordings; where they are not available we say so and do not generalise.
- Recorded logs with injected faults are semi synthetic. They are labelled as such.
- No hardware, no certification, no legal conclusion. The author of the monitor, the generator and the thresholds is the same person; a second coder and a second scorer limit this and do not remove it.

## Order of fixing, so that nothing is tuned to the result

1. This page committed.
2. Human check design and sample frame committed (done: `data/human_check/DESIGN.md`).
3. Silence audit codebook committed before any row is coded.
4. Round 3 preregistration committed, then registered on a public registry that issues its own timestamp, before any recorded log is replayed.
5. Replay, scoring, reporting of every prediction including the failed ones.

## Amendments

None yet.
