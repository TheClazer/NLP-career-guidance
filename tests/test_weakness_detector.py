import unittest
from intelligence.weakness_detector import score_sentence_strength

class TestWeakness(unittest.TestCase):
    def test_detect_no_metrics(self):
        sent = "Worked on machine learning pipeline and improved features."
        r = score_sentence_strength(sent, ["Machine Learning"], top_role_skills=["Machine Learning"])
        # Expect penalty for no metrics
        self.assertIn("no measurable result", r["reasons"])
        self.assertTrue(r["severity"] > 20)

    def test_detect_strong_sentence(self):
        sent = "Improved model F1 by 12% by redesigning the feature pipeline and reducing runtime by 40%."
        r = score_sentence_strength(sent, ["Machine Learning"], top_role_skills=["Machine Learning"])
        # Expect low severity
        self.assertTrue(r["severity"] < 40)
        
    def test_hedging_penalty(self):
        sent = "I somewhat helped with the database migration."
        r = score_sentence_strength(sent, [], [])
        self.assertIn("hedging / weak phrasing", r["reasons"])

if __name__ == '__main__':
    unittest.main()
