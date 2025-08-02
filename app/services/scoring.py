# Scoring logic for hackathon
# TODO: Implement document/question weight logic as per rules

def calculate_score(is_correct: bool, doc_weight: float, q_weight: float) -> float:
    if not is_correct:
        return 0.0
    return doc_weight * q_weight
