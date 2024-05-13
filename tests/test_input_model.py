from json_generator.data_module import InputModel, placeholder


def test_to_prompt():
    class LegalPassage(InputModel):
        input_prompt: str = "{$DOC_DOMAIN} - {$DOC_SOURCE} - {$DOC_GROUNDED_CONTENT}"
        domain: str = placeholder("{$DOC_DOMAIN}")
        metadata: str = placeholder("{$DOC_SOURCE}")
        grounded_content: str = placeholder("{$DOC_GROUNDED_CONTENT}")

    legal_passage = LegalPassage(
        domain="CIVIL",
        metadata="Bộ luật dân sự 2015",
        grounded_content="Người có nghĩa vụ trả tiền thuê nhà phải trả tiền thuê đúng hạn, trừ trường hợp có thoả thuận khác.",
    )

    assert (
        legal_passage.to_prompt()
        == "CIVIL - Bộ luật dân sự 2015 - Người có nghĩa vụ trả tiền thuê nhà phải trả tiền thuê đúng hạn, trừ trường hợp có thoả thuận khác."
    )
