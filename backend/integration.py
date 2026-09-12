from concurrent.futures import ThreadPoolExecutor, as_completed

from Classification.classifier_wizard import (
    WizardInput,
    classify_product
)

from IP.ip_checker import IPChecker
from Regulatory.regulatory_fitcheck import RegulatoryFitCheck
from TKDL.tkdl_check import TKDLCheck
from ABS.abs_check import ABSCheck


class IPShaktiOrchestrator:
    """
    Main integration/orchestration layer for IP-SHAKTI Sahayak.

    Flow:

        Wizard Input
              ↓
        Classification
              ↓
         ProductContext
              ↓
        ┌─────┼─────┬─────┐
        ↓     ↓     ↓     ↓
       IP    REG   TKDL   ABS
        └─────┼─────┴─────┘
              ↓
       Combined Assessment
    """

    def __init__(self):
        """
        Initialize the assessment modules.

        Existing module logic is not changed.
        """

        self.ip_checker = IPChecker()
        self.regulatory_checker = RegulatoryFitCheck()
        self.tkdl_checker = TKDLCheck()
        self.abs_checker = ABSCheck()

    # --------------------------------------------------
    # Classification
    # --------------------------------------------------

    def classify(self, wizard_input: WizardInput):
        """
        Convert wizard input into the ProductContext used
        by the downstream modules.
        """

        product_context = classify_product(wizard_input)

        return product_context

    # --------------------------------------------------
    # Individual assessment functions
    # --------------------------------------------------

    def run_ip(self, product_context):
        """
        Run IP screening.
        """

        return self.ip_checker.check_ip(
            product_context
        )

    def run_regulatory(self, product_context):
        """
        Run Regulatory FitCheck.
        """

        return self.regulatory_checker.assess(
            product_context
        )

    def run_tkdl(self, product_context):
        """
        Run TKDL assessment.
        """

        return self.tkdl_checker.assess(
            product_context
        )

    def run_abs(self, product_context):
        """
        Run ABS assessment.
        """

        return self.abs_checker.assess(
            product_context
        )

    # --------------------------------------------------
    # Parallel assessment
    # --------------------------------------------------

    def run_assessments(self, product_context):
        """
        Run IP, Regulatory, TKDL and ABS independently
        and in parallel.

        None of these modules depends on the result of
        another module.
        """

        assessments = {}

        tasks = {
            "ip_assessment": self.run_ip,
            "regulatory_assessment": self.run_regulatory,
            "tkdl_assessment": self.run_tkdl,
            "abs_assessment": self.run_abs
        }

        with ThreadPoolExecutor(
            max_workers=4
        ) as executor:

            futures = {
                executor.submit(
                    function,
                    product_context
                ): name
                for name, function in tasks.items()
            }

            for future in as_completed(futures):

                assessment_name = futures[future]

                try:
                    assessments[assessment_name] = (
                        future.result()
                    )

                except Exception as e:

                    assessments[assessment_name] = {
                        "status": "error",
                        "error": str(e)
                    }

        return assessments

    # --------------------------------------------------
    # Complete workflow
    # --------------------------------------------------

    def run(self, wizard_input: WizardInput):
        """
        Execute the complete assessment workflow.

        Roadmap is intentionally NOT included yet.
        We will connect it after the integration layer
        is working.
        """

        # ----------------------------------------------
        # 1. Classification
        # ----------------------------------------------

        product_context = self.classify(
            wizard_input
        )

        # ----------------------------------------------
        # 2. Parallel assessment
        # ----------------------------------------------

        assessments = self.run_assessments(
            product_context
        )

        # ----------------------------------------------
        # 3. Combined assessment
        # ----------------------------------------------

        result = {
            "product_context": product_context,

            "ip_assessment": assessments.get(
                "ip_assessment"
            ),

            "regulatory_assessment": assessments.get(
                "regulatory_assessment"
            ),

            "tkdl_assessment": assessments.get(
                "tkdl_assessment"
            ),

            "abs_assessment": assessments.get(
                "abs_assessment"
            )
        }

        return result


# ------------------------------------------------------
# Convenience function
# ------------------------------------------------------

def run_ip_shakti(wizard_input: WizardInput):
    """
    Simple function for the frontend/FastAPI layer.

    Example:

        result = run_ip_shakti(wizard_input)
    """

    orchestrator = IPShaktiOrchestrator()

    return orchestrator.run(
        wizard_input
    )