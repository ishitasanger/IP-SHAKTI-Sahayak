from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# =========================================================
# ALLOWED VALUES
# =========================================================

PRODUCT_TYPES = {
    "ayurvedic medicine",
    "herbal medicine",
    "nutraceutical",
    "food product",
    "dietary supplement",
    "cosmetic",
    "personal care product",
    "other",
}


CLASSIFICATIONS = {
    "classical / traditional formulation",
    "proprietary formulation",
    "single ingredient product",
    "multi-ingredient formulation",
    "not sure",
}


TRADITIONAL_KNOWLEDGE_OPTIONS = {
    "yes",
    "no",
    "not sure",
}


BIOLOGICAL_RESOURCE_OPTIONS = {
    "yes",
    "no",
    "not sure",
}


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def clean_string(value: str) -> str:
    """
    Remove unnecessary whitespace from a string.
    """

    return " ".join(value.strip().split())


def clean_list(items: List[str]) -> List[str]:
    """
    Clean a list of strings.

    - Removes empty values
    - Removes unnecessary whitespace
    - Removes duplicates
    - Preserves original order
    """

    cleaned_items = []
    seen = set()

    for item in items:

        if not isinstance(item, str):
            continue

        cleaned_item = clean_string(item)

        if not cleaned_item:
            continue

        key = cleaned_item.lower()

        if key not in seen:
            cleaned_items.append(cleaned_item)
            seen.add(key)

    return cleaned_items


def normalize_option(value: str) -> str:
    """
    Normalize controlled option values.

    Example:
        ' Ayurvedic Medicine '
        ->
        'ayurvedic medicine'
    """

    return clean_string(value).lower()


# =========================================================
# WIZARD INPUT
# =========================================================

class WizardInput(BaseModel):
    """
    Raw information collected from the frontend
    Classification Wizard.

    The wizard collects and structures product facts.

    It does NOT make legal conclusions.
    """


    # -----------------------------------------------------
    # BASIC PRODUCT INFORMATION
    # -----------------------------------------------------

    product_name: str

    product_description: Optional[str] = None

    jurisdiction: str = "India"


    # -----------------------------------------------------
    # PRODUCT CLASSIFICATION
    # -----------------------------------------------------

    product_type: str

    classification: str

    form: Optional[str] = None


    # -----------------------------------------------------
    # FORMULATION
    # -----------------------------------------------------

    ingredients: List[str] = Field(
        default_factory=list
    )


    # -----------------------------------------------------
    # PURPOSE AND CLAIMS
    # -----------------------------------------------------

    intended_use: str

    claims: List[str] = Field(
        default_factory=list
    )


    # -----------------------------------------------------
    # INNOVATION INFORMATION
    # -----------------------------------------------------

    innovation_description: Optional[str] = None


    # -----------------------------------------------------
    # TRADITIONAL KNOWLEDGE
    # -----------------------------------------------------

    traditional_knowledge: str = "not sure"

    traditional_knowledge_source: Optional[str] = None


    # -----------------------------------------------------
    # BIOLOGICAL RESOURCES
    # -----------------------------------------------------

    uses_biological_resources: str = "not sure"

    biological_resources: List[str] = Field(
        default_factory=list
    )


    # -----------------------------------------------------
    # COMMERCIAL INFORMATION
    # -----------------------------------------------------

    manufacturing_location: Optional[str] = None

    commercial_use: bool = True


    # =====================================================
    # STRING VALIDATION
    # =====================================================

    @field_validator(
        "product_name",
        "product_description",
        "jurisdiction",
        "product_type",
        "classification",
        "form",
        "intended_use",
        "innovation_description",
        "traditional_knowledge",
        "traditional_knowledge_source",
        "uses_biological_resources",
        "manufacturing_location",
        mode="before"
    )
    @classmethod
    def validate_strings(cls, value):

        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError(
                "Expected a string value."
            )

        cleaned_value = clean_string(value)

        return cleaned_value


    # =====================================================
    # LIST VALIDATION
    # =====================================================

    @field_validator(
        "ingredients",
        "claims",
        "biological_resources",
        mode="before"
    )
    @classmethod
    def validate_lists(cls, value):

        if value is None:
            return []

        if not isinstance(value, list):
            raise ValueError(
                "Expected a list."
            )

        return clean_list(value)


    # =====================================================
    # PRODUCT TYPE VALIDATION
    # =====================================================

    @field_validator("product_type")
    @classmethod
    def validate_product_type(cls, value):

        normalized = normalize_option(value)

        if normalized not in PRODUCT_TYPES:

            allowed = ", ".join(
                sorted(PRODUCT_TYPES)
            )

            raise ValueError(
                "Invalid product_type. "
                f"Allowed values are: {allowed}"
            )

        return normalized


    # =====================================================
    # CLASSIFICATION VALIDATION
    # =====================================================

    @field_validator("classification")
    @classmethod
    def validate_classification(cls, value):

        normalized = normalize_option(value)

        if normalized not in CLASSIFICATIONS:

            allowed = ", ".join(
                sorted(CLASSIFICATIONS)
            )

            raise ValueError(
                "Invalid classification. "
                f"Allowed values are: {allowed}"
            )

        return normalized


    # =====================================================
    # TRADITIONAL KNOWLEDGE VALIDATION
    # =====================================================

    @field_validator("traditional_knowledge")
    @classmethod
    def validate_traditional_knowledge(
        cls,
        value
    ):

        normalized = normalize_option(value)

        if (
            normalized
            not in TRADITIONAL_KNOWLEDGE_OPTIONS
        ):
            raise ValueError(
                "traditional_knowledge must be: "
                "yes, no, or not sure"
            )

        return normalized


    # =====================================================
    # BIOLOGICAL RESOURCE VALIDATION
    # =====================================================

    @field_validator("uses_biological_resources")
    @classmethod
    def validate_biological_resources(
        cls,
        value
    ):

        normalized = normalize_option(value)

        if (
            normalized
            not in BIOLOGICAL_RESOURCE_OPTIONS
        ):
            raise ValueError(
                "uses_biological_resources must be: "
                "yes, no, or not sure"
            )

        return normalized


# =========================================================
# PRODUCT CONTEXT
# =========================================================

class ProductContext(BaseModel):
    """
    Standardized product context.

    This is the contract between the Classification Wizard
    and downstream backend modules.

    Possible consumers:

        - TKDL
        - ABS
        - Regulatory
        - IP Checking
        - RAG Pipeline
    """


    # -----------------------------------------------------
    # BASIC INFORMATION
    # -----------------------------------------------------

    product_name: str

    product_description: Optional[str] = None

    jurisdiction: str


    # -----------------------------------------------------
    # PRODUCT CLASSIFICATION
    # -----------------------------------------------------

    product_type: str

    classification: str

    form: Optional[str] = None


    # -----------------------------------------------------
    # FORMULATION
    # -----------------------------------------------------

    ingredients: List[str]

    ingredient_count: int


    # -----------------------------------------------------
    # PURPOSE AND CLAIMS
    # -----------------------------------------------------

    intended_use: str

    claims: List[str]


    # -----------------------------------------------------
    # INNOVATION
    # -----------------------------------------------------

    innovation_description: Optional[str] = None


    # -----------------------------------------------------
    # TRADITIONAL KNOWLEDGE
    # -----------------------------------------------------

    traditional_knowledge: str

    traditional_knowledge_source: Optional[str] = None


    # -----------------------------------------------------
    # BIOLOGICAL RESOURCES
    # -----------------------------------------------------

    uses_biological_resources: str

    biological_resources: List[str]


    # -----------------------------------------------------
    # COMMERCIAL INFORMATION
    # -----------------------------------------------------

    manufacturing_location: Optional[str] = None

    commercial_use: bool


# =========================================================
# CONSISTENCY VALIDATION
# =========================================================

def validate_consistency(
    wizard_input: WizardInput
):
    """
    Check for logical contradictions.

    These are data consistency checks.

    They are NOT legal assessments.
    """

    errors = []


    # -----------------------------------------------------
    # PRODUCT NAME
    # -----------------------------------------------------

    if not wizard_input.product_name:
        errors.append(
            "Product name cannot be empty."
        )


    # -----------------------------------------------------
    # INGREDIENT CHECK
    # -----------------------------------------------------

    if (
        wizard_input.classification
        == "single ingredient product"
        and len(wizard_input.ingredients) != 1
    ):
        errors.append(
            "A single ingredient product must "
            "contain exactly one ingredient."
        )


    # -----------------------------------------------------
    # BIOLOGICAL RESOURCES
    # -----------------------------------------------------

    if (
        wizard_input.uses_biological_resources
        == "no"
        and len(
            wizard_input.biological_resources
        ) > 0
    ):
        errors.append(
            "Biological resources were provided "
            "but uses_biological_resources is 'no'."
        )


    if (
        wizard_input.uses_biological_resources
        == "yes"
        and len(
            wizard_input.biological_resources
        ) == 0
    ):
        errors.append(
            "uses_biological_resources is 'yes' "
            "but no biological resources were provided."
        )


    # -----------------------------------------------------
    # TRADITIONAL KNOWLEDGE
    # -----------------------------------------------------

    if (
        wizard_input.traditional_knowledge
        == "no"
        and wizard_input.traditional_knowledge_source
    ):
        errors.append(
            "A traditional knowledge source was "
            "provided but traditional_knowledge "
            "is 'no'."
        )


    # -----------------------------------------------------
    # FINAL ERROR HANDLING
    # -----------------------------------------------------

    if errors:
        raise ValueError(
            "\n".join(errors)
        )


# =========================================================
# BUILD PRODUCT CONTEXT
# =========================================================

def build_product_context(
    wizard_input: WizardInput
) -> ProductContext:
    """
    Convert WizardInput into standardized ProductContext.
    """

    validate_consistency(
        wizard_input
    )


    ingredient_count = len(
        wizard_input.ingredients
    )


    product_context = ProductContext(

        # Basic information
        product_name=wizard_input.product_name,

        product_description=(
            wizard_input.product_description
        ),

        jurisdiction=wizard_input.jurisdiction,


        # Classification
        product_type=wizard_input.product_type,

        classification=(
            wizard_input.classification
        ),

        form=wizard_input.form,


        # Formulation
        ingredients=wizard_input.ingredients,

        ingredient_count=ingredient_count,


        # Purpose
        intended_use=wizard_input.intended_use,

        claims=wizard_input.claims,


        # Innovation
        innovation_description=(
            wizard_input.innovation_description
        ),


        # Traditional knowledge
        traditional_knowledge=(
            wizard_input.traditional_knowledge
        ),

        traditional_knowledge_source=(
            wizard_input
            .traditional_knowledge_source
        ),


        # Biological resources
        uses_biological_resources=(
            wizard_input
            .uses_biological_resources
        ),

        biological_resources=(
            wizard_input
            .biological_resources
        ),


        # Commercial information
        manufacturing_location=(
            wizard_input
            .manufacturing_location
        ),

        commercial_use=(
            wizard_input.commercial_use
        )
    )


    return product_context


# =========================================================
# MAIN CLASSIFICATION FUNCTION
# =========================================================

def classify_product(
    wizard_input: WizardInput
) -> ProductContext:
    """
    Main entry point.

    The Classification Wizard collects facts,
    validates them, and returns ProductContext.

    No legal decision is made here.
    """

    return build_product_context(
        wizard_input
    )
