from json_generator.data_module import OutputModel


def test_output_model():
    class LegalQuery(OutputModel):
        aspects: list[str]
        questions: list[str]

        @classmethod
        def empty(cls) -> "LegalQuery":
            return LegalQuery(aspects=[], questions=[])

    legal_query = LegalQuery(
        aspects=["Aspect 1", "Aspect 2"], questions=["Question 1", "Question 2"]
    )

    assert legal_query.aspects == ["Aspect 1", "Aspect 2"]
    assert legal_query.questions == ["Question 1", "Question 2"]

    empty_legal_query = LegalQuery.empty()

    assert empty_legal_query.aspects == []
    assert empty_legal_query.questions == []
