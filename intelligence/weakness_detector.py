import re
from typing import List, Dict

HEDGING_WORDS = ["maybe","kind of","somewhat","a bit","possibly","helped","assisted","familiar with"]
PASSIVE_PATTERN = re.compile(r"\b(was|were|is|are|been|being)\b\s+\w+ed\b", re.I)
NUMERIC_RE = re.compile(r'\b\d+%?|\b\d+\s+(?:hours|days|users|clients|transactions|months|years)\b', re.I)
STRONG_VERBS = ["built","led","improved","developed","reduced","increased","implemented","designed","deployed","optimized"]

def score_sentence_strength(sent: str, detected_skills: List[str], top_role_skills: List[str]=None) -> Dict:
    sent_low = sent.lower()
    score = 1.0
    reasons = []

    # numeric evidence
    if not NUMERIC_RE.search(sent):
        score -= 0.35
        reasons.append("no measurable result")

    # hedging / weak language
    if any(w in sent_low for w in HEDGING_WORDS):
        score -= 0.2
        reasons.append("hedging / weak phrasing")

    # passive voice
    if PASSIVE_PATTERN.search(sent):
        score -= 0.15
        reasons.append("passive voice")

    # strong verb check
    if not any(v in sent_low for v in STRONG_VERBS):
        score -= 0.1
        reasons.append("no strong action verb")

    # if role skills provided, check if sentence includes any top_role_skills
    if top_role_skills:
        overlap = sum(1 for s in top_role_skills if s.lower() in sent_low)
        if overlap == 0:
            score -= 0.15
            reasons.append("missing role-relevant keywords")
        else:
            # reward small boost for relevance
            score += min(0.08, 0.02 * overlap)

    # clamp
    score = max(0.0, min(1.0, score))
    severity = int((1.0 - score) * 100)  # 0=good, 100=very weak
    return {"sentence": sent, "score": score, "severity": severity, "reasons": reasons}
