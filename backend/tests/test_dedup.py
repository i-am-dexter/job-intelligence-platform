from app.services.dedup import compute_dedup_hash


def test_same_inputs_produce_same_hash():
    a = compute_dedup_hash("Stripe", "Software Engineer", "Remote")
    b = compute_dedup_hash("Stripe", "Software Engineer", "Remote")
    assert a == b


def test_case_and_whitespace_insensitive():
    a = compute_dedup_hash("Stripe", "Software Engineer", "Remote")
    b = compute_dedup_hash("  stripe ", " software engineer ", " remote ")
    assert a == b


def test_different_inputs_produce_different_hash():
    a = compute_dedup_hash("Stripe", "Software Engineer", "Remote")
    b = compute_dedup_hash("Stripe", "Senior Software Engineer", "Remote")
    assert a != b
