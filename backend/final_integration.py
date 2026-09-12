from integration import IPShaktiOrchestrator
from Roadmap.roadmap import RoadmapGenerator


class FinalIntegration:

    def __init__(self):
        self.orchestrator = IPShaktiOrchestrator()
        self.roadmap_generator = RoadmapGenerator()

    def run(self, wizard_input):

        # Step 1: Run the four assessments
        assessment = self.orchestrator.run(wizard_input)

        # Step 2: Generate roadmap from those results
        roadmap = self.roadmap_generator.generate(
            ip_assessment=assessment.get("ip_assessment"),
            regulatory_assessment=assessment.get("regulatory_assessment"),
            tkdl_assessment=assessment.get("tkdl_assessment"),
            abs_assessment=assessment.get("abs_assessment")
        )

        # Step 3: Add roadmap to final response
        assessment["roadmap"] = roadmap

        return assessment