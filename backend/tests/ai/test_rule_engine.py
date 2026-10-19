from app.ai.rule_engine import RuleEngine


def test_rule_engine_safe():
    engine = RuleEngine()
    text = "Subject: Weekly update\n\nHere are the notes from our weekly team meeting. Thanks!"
    matches = engine.analyze(text)

    assert len(matches) == 0

    label, probs = engine.classify(matches)
    assert label == "safe"
    assert probs["safe"] > 0.8

    risk = engine.compute_risk_score(matches)
    assert risk == 0.0

def test_rule_engine_phishing():
    engine = RuleEngine()
    text = "Subject: Urgent Account Suspension\n\nYour PayPal account has been limited. Click here to verify your identity immediately: http://paypa1-secure.tk/verify"
    matches = engine.analyze(text)

    assert len(matches) > 0
    # Should match urgency, brand impersonation, and link
    categories = {m.category for m in matches}
    assert "urgency" in categories
    assert "credential_harvesting" in categories
    assert "link_manipulation" in categories

    label, probs = engine.classify(matches)
    assert label == "phishing"
    assert probs["phishing"] > 0.7

    risk = engine.compute_risk_score(matches)
    assert risk > 50.0
