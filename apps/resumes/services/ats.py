import re
REQUIRED_SECTIONS = ['experience', 'education', 'skills']
ACTION_VERBS = ['built','developed','designed','implemented','optimized','led','created','improved','managed','integrated']

def rule_based_score(text: str, role_keywords: list[str]) -> dict:
    lower = text.lower()
    score = 0; issues=[]
    section_hits = sum(1 for s in REQUIRED_SECTIONS if s in lower)
    score += int((section_hits / len(REQUIRED_SECTIONS)) * 25)
    if section_hits < len(REQUIRED_SECTIONS): issues.append('Missing common resume sections.')
    keyword_hits = sum(1 for kw in role_keywords if kw.lower() in lower)
    score += min(30, keyword_hits * 4)
    if keyword_hits < 4: issues.append('Low role keyword coverage.')
    bullet_like = len(re.findall(r'(^|\n)\s*[-•*]', text))
    score += min(20, bullet_like * 2)
    if bullet_like < 5: issues.append('Few bullet points detected.')
    verb_hits = sum(1 for v in ACTION_VERBS if v in lower)
    score += min(15, verb_hits * 3)
    measurable = len(re.findall(r'\d+%?|\$\d+|\d+k\+?', lower))
    score += min(10, measurable * 2)
    if measurable < 2: issues.append('Add more measurable impact metrics.')
    return {'score': max(0, min(100, score)), 'issues': issues, 'keyword_hits': keyword_hits}

def hybrid_score(rule_score: int, ai_score: int) -> int:
    return round(rule_score * 0.4 + ai_score * 0.6)
