import unittest
from nlp.skill_extractor import extract_skills_with_evidence

class TestNLP(unittest.TestCase):
    def test_basic_extraction(self):
        text = "I have experience with Python and SQL."
        # Note: Ensure your ontology has these keys for this test to pass
        # The extract_skills_with_evidence function requires a keywords list
        keywords = ["Python", "SQL"]
        skills_data = extract_skills_with_evidence(text, keywords)
        
        extracted_names = [s["name"] for s in skills_data]
        
        self.assertIn("python", extracted_names) # The extractor returns lowercase keys
        self.assertIn("sql", extracted_names)

    def test_case_insensitivity(self):
        text = "i know python."
        keywords = ["Python"]
        skills_data = extract_skills_with_evidence(text, keywords)
        
        extracted_names = [s["name"] for s in skills_data]
        self.assertIn("python", extracted_names)

if __name__ == '__main__':
    unittest.main()
