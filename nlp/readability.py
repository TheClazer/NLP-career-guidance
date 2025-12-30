import textstat

def readability_score(text):
    if not text.strip():
        return 0.0
    return round(textstat.flesch_kincaid_grade(text), 2)
