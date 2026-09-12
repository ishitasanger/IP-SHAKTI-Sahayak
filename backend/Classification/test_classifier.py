from Classification.classifier_wizard import (
    WizardInput,
    classify_product
)


# =========================================================
# HELPER FUNCTION
# =========================================================

def print_result(title, result):

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)

    print("\nPRODUCT CONTEXT:\n")

    print(
        result.model_dump_json(
            indent=4
        )
    )


# =========================================================
# TEST 1
# AYURVEDIC FORMULATION
# =========================================================

def test_ayurvedic_formulation():

    wizard_input = WizardInput(

        product_name=(
            "Ashwagandha Wellness Capsules"
        ),

        product_description=(
            "A herbal capsule containing "
            "Ashwagandha and Guduchi intended "
            "to support general wellness and "
            "stress management."
        ),

        jurisdiction="India",


        product_type=(
            "Ayurvedic medicine"
        ),

        classification=(
            "Proprietary formulation"
        ),

        form="Capsule",


        ingredients=[
            "Ashwagandha",
            "Guduchi",
            "Ashwagandha"
        ],


        intended_use=(
            "Supports general wellness and "
            "stress management"
        ),

        claims=[
            "Supports stress relief",
            "Improves general wellness",
            "Supports stress relief"
        ],


        innovation_description=(
            "The product combines Ashwagandha "
            "and Guduchi in a specific formulation "
            "intended for stress management."
        ),


        traditional_knowledge="Yes",

        traditional_knowledge_source=(
            "Traditional Ayurvedic knowledge"
        ),


        uses_biological_resources="Yes",

        biological_resources=[
            "Ashwagandha",
            "Guduchi"
        ],


        manufacturing_location="India",

        commercial_use=True
    )


    result = classify_product(
        wizard_input
    )


    print_result(
        "TEST 1: AYURVEDIC FORMULATION",
        result
    )


# =========================================================
# TEST 2
# COSMETIC PRODUCT
# =========================================================

def test_cosmetic_product():

    wizard_input = WizardInput(

        product_name=(
            "Herbal Glow Face Cream"
        ),

        product_description=(
            "A cosmetic cream containing "
            "plant-based ingredients for "
            "skin care."
        ),

        jurisdiction="India",


        product_type="Cosmetic",

        classification=(
            "Multi-ingredient formulation"
        ),

        form="Cream",


        ingredients=[
            "Aloe Vera",
            "Neem",
            "Turmeric"
        ],


        intended_use=(
            "Skin care and cosmetic use"
        ),

        claims=[
            "Improves skin appearance",
            "Supports healthy looking skin"
        ],


        innovation_description=(
            "A combination of herbal ingredients "
            "designed for cosmetic skin care."
        ),


        traditional_knowledge="Not sure",


        uses_biological_resources="Yes",

        biological_resources=[
            "Aloe Vera",
            "Neem",
            "Turmeric"
        ],


        manufacturing_location="India",

        commercial_use=True
    )


    result = classify_product(
        wizard_input
    )


    print_result(
        "TEST 2: COSMETIC PRODUCT",
        result
    )


# =========================================================
# TEST 3
# SINGLE INGREDIENT PRODUCT
# =========================================================

def test_single_ingredient_product():

    wizard_input = WizardInput(

        product_name=(
            "Pure Turmeric Powder"
        ),

        product_description=(
            "A single ingredient turmeric powder "
            "intended for food use."
        ),

        jurisdiction="India",


        product_type="Food product",

        classification=(
            "Single ingredient product"
        ),

        form="Powder",


        ingredients=[
            "Turmeric"
        ],


        intended_use=(
            "Food and nutritional use"
        ),

        claims=[
            "Natural food ingredient"
        ],


        innovation_description=None,


        traditional_knowledge="Not sure",


        uses_biological_resources="Yes",

        biological_resources=[
            "Turmeric"
        ],


        manufacturing_location="India",

        commercial_use=True
    )


    result = classify_product(
        wizard_input
    )


    print_result(
        "TEST 3: SINGLE INGREDIENT PRODUCT",
        result
    )


# =========================================================
# TEST 4
# INVALID SINGLE INGREDIENT PRODUCT
# =========================================================

def test_invalid_single_ingredient():

    print("\n")
    print("=" * 70)
    print(
        "TEST 4: CONSISTENCY VALIDATION"
    )
    print("=" * 70)


    try:

        wizard_input = WizardInput(

            product_name="Test Product",

            jurisdiction="India",


            product_type=(
                "Herbal medicine"
            ),

            classification=(
                "Single ingredient product"
            ),


            ingredients=[
                "Ashwagandha",
                "Guduchi"
            ],


            intended_use=(
                "General wellness"
            ),


            traditional_knowledge=(
                "Not sure"
            ),


            uses_biological_resources=(
                "Not sure"
            )
        )


        classify_product(
            wizard_input
        )


    except Exception as error:

        print(
            "\nEXPECTED ERROR:\n"
        )

        print(error)


# =========================================================
# TEST 5
# BIOLOGICAL RESOURCE CONSISTENCY
# =========================================================

def test_invalid_biological_resources():

    print("\n")
    print("=" * 70)
    print(
        "TEST 5: BIOLOGICAL RESOURCE VALIDATION"
    )
    print("=" * 70)


    try:

        wizard_input = WizardInput(

            product_name="Test Product",

            jurisdiction="India",


            product_type=(
                "Herbal medicine"
            ),

            classification=(
                "Multi-ingredient formulation"
            ),


            ingredients=[
                "Ashwagandha"
            ],


            intended_use=(
                "General wellness"
            ),


            traditional_knowledge=(
                "Not sure"
            ),


            uses_biological_resources=(
                "Yes"
            ),


            biological_resources=[]
        )


        classify_product(
            wizard_input
        )


    except Exception as error:

        print(
            "\nEXPECTED ERROR:\n"
        )

        print(error)


# =========================================================
# RUN ALL TESTS
# =========================================================

def run_all_tests():

    print("\n")
    print("#" * 70)
    print(
        "CLASSIFICATION WIZARD TEST SUITE"
    )
    print("#" * 70)


    test_ayurvedic_formulation()

    test_cosmetic_product()

    test_single_ingredient_product()

    test_invalid_single_ingredient()

    test_invalid_biological_resources()


    print("\n")
    print("#" * 70)
    print(
        "ALL TESTS COMPLETED"
    )
    print("#" * 70)


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    run_all_tests()
