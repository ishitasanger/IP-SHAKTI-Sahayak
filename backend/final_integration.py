from typing import Any
from .integration import IPShaktiOrchestrator
from .Roadmap.roadmap import RoadmapGenerator


def normalize_assessment(value: Any) -> Any:
    """
    Boundary-normalization helper that converts Pydantic models to dictionaries.
    - If a value supports model_dump(), use value.model_dump().
    - If it is already a dictionary, keep it unchanged.
    - Otherwise leave it unchanged.
    """
    if hasattr(value, "model_dump") and callable(getattr(value, "model_dump")):
        return value.model_dump()
    if isinstance(value, dict):
        return value
    if hasattr(value, "to_dict") and callable(getattr(value, "to_dict")):
        return value.to_dict()
    return value


class FinalIntegration:

    def __init__(self):
        self.orchestrator = IPShaktiOrchestrator()
        self.roadmap_generator = RoadmapGenerator()

    def run(self, wizard_input):

        # Step 1: Run the four assessments
        assessment = self.orchestrator.run(wizard_input)

        # Boundary normalization: convert Pydantic models / result objects to dicts
        ip_assessment = normalize_assessment(assessment.get("ip_assessment"))
        regulatory_assessment = normalize_assessment(assessment.get("regulatory_assessment"))
        tkdl_assessment = normalize_assessment(assessment.get("tkdl_assessment"))
        abs_assessment = normalize_assessment(assessment.get("abs_assessment"))

        # Step 2: Generate roadmap from those results
        roadmap = self.roadmap_generator.generate(
            ip_assessment=ip_assessment,
            regulatory_assessment=regulatory_assessment,
            tkdl_assessment=tkdl_assessment,
            abs_assessment=abs_assessment
        )

        # Step 3: Add normalized assessments and roadmap to final response
        assessment["ip_assessment"] = ip_assessment
        assessment["regulatory_assessment"] = regulatory_assessment
        assessment["tkdl_assessment"] = tkdl_assessment
        assessment["abs_assessment"] = abs_assessment
        assessment["roadmap"] = roadmap

        return assessment