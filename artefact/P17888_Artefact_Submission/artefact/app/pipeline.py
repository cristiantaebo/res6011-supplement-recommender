"""Core interpreter-to-engine pipeline. No HTTP or UI behavior is defined here."""

from app.engine import DecisionEngine
from app.interpreter import ControlledInterpreter, MAX_INPUT_LENGTH, _contains_phrase, normalize_text


class CorePipeline:
    def __init__(self, repository):
        self.repository = repository
        self.interpreter = ControlledInterpreter(repository)
        self.engine = DecisionEngine(repository)

    def process(self, user_input: object) -> dict:
        # Request policy is stricter than the interpreter's exact-alias matcher.
        # These two finite noun forms close demonstrated medical-boundary gaps;
        # they do not claim general semantic understanding or change seed facts.
        if isinstance(user_input, str) and len(user_input) <= MAX_INPUT_LENGTH:
            normalized = normalize_text(user_input)
            noun_forms = {"diagnose": "diagnosis", "treat": "treatment"}
            for boundary in self.repository.boundary_patterns():
                noun = noun_forms.get(normalize_text(boundary["phrase"]))
                if noun and _contains_phrase(normalized, noun):
                    return {
                        "status": "BOUNDARY",
                        "pattern_id": boundary["pattern_id"],
                        "boundary_code": boundary["boundary_code"],
                        "message": boundary["response_text"],
                    }
        interpretation = self.interpreter.interpret(user_input)
        if interpretation["status"] != "OK":
            return interpretation
        term_ids = [item["term_id"] for item in interpretation["matched_terms"]]
        decision = self.engine.recommend(term_ids)
        return {
            "status": decision["status"],
            "data_version": decision["data_version"],
            "applied_exclusions": decision["applied_exclusions"],
            "matched_terms": interpretation["matched_terms"],
            "recommendations": decision["recommendations"],
            "message": decision["message"],
        }
