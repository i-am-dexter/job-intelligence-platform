from app.services.skills_taxonomy import extract_skills_from_text


def test_extracts_known_skills():
    text = "We use Python, React, and AWS extensively."
    skills = extract_skills_from_text(text)
    assert "python" in skills
    assert "react" in skills
    assert "aws" in skills


def test_does_not_match_substring_false_positive():
    # "java" must not match inside "javascript"
    skills = extract_skills_from_text("Experience with JavaScript required.")
    assert "java" not in skills
    assert "javascript" in skills


def test_empty_text_returns_empty_list():
    assert extract_skills_from_text("") == []
    assert extract_skills_from_text(None) == []
