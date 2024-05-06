input_prompt = """You are an advanced legal query generator with specialized skills in analyzing legal documents. When provided with an excerpt from a legal document, your task is to identify 1-5 critical aspects or implications that might interest or impact the readers. These aspects should address various dimensions of the content, focusing on rights, obligations, potential legal issues, or general legal awareness, exclusively within provided grounded content. Do not consider information in document's source for this analysis. The following is the mentioned excerpt:

<document>
<domain>{$DOC_DOMAIN}</domain>
<source>{$DOC_SOURCE}</source>
<content>{$DOC_GROUNDED_CONTENT}</content>
</document>

For each identified critical aspect, generate a single question. These questions should reflect plausible inquiries that an average citizen might have, relating directly to the document but formulated in a manner accessible to someone unfamiliar with the presence of the legal text or information being asked about. Phrase the questions as if coming from a layperson who has not read or seen the legal text ever.

Your output should be in JSON format, listing the critical aspects identified and a corresponding question for each aspect. Please adhere to the following guidelines for creating questions:
- Think creatively about real-world scenarios and edge cases the law might apply to, phrase it naturally as if asked by an average citizen.
- The queries should be ones that could reasonably be answered by the information exclusively within provided grounded content only. Do not ask information in document's source.
- Each query should be one sentence only and its length is no more than 120 words.
- Try to phrase each of the question as detailed as possible, as if you haven't never seen the legal text and are trying to looking for it using keywords in the question, you may need to include details in document's source and domain for this aim. You should not quote the exact legal text code (like 02/2017/TT-BQP). The better way is to include information on the content of document as in document's source instead like the executive body published the document (e.g. "Bộ Y tế quy định thế nào về ..."). In the case you have to refer to the legal text, use words like: "Quy định pháp luật", "Pháp luật", "Luật". Don't use the word "này".
- Present your analysis and questions in Vietnamese.

<example>
<description>Bad questions refer to the legal text directly</description>
<bad_question>Thông tư này quy định những nguyên tắc gì trong việc thi hành án tử hình bằng hình thức tiêm thuốc độc?</bad_question>
<good_question>Pháp luật quy định những nguyên tắc gì trong việc thi hành án tử hình bằng hình thức tiêm thuốc độc?</good_question>
<best_question>Thông tư do Bộ Công an ban hành quy định những nguyên tắc gì trong việc thi hành án tử hình bằng hình thức tiêm thuốc độc?</best_question>
</example>

<example>
<description>Bad questions does not include enough context or detail</description>
<bad_question>Theo quy định, người được khám giám định không đồng ý với kết quả khám giám định phúc quyết của Hội đồng Giám định Y khoa cấp Trung ương thì sẽ được xử lý như thế nào?</bad_question>
<good_question>Nếu người bị phơi nhiễm chất độc hóa học trong kháng chiến không đồng ý với kết quả giám định của Hội đồng GĐYK cấp Trung ương, họ có thể làm gì để được xem xét lại?</good_question>
</example>

Structure your output in the JSON format below:
```
{
  "aspects": [
    [Brief description of the aspect 1],
    [Brief description of the aspect 2],
    ...
  ],
  "questions": [
    [Your question related to aspect 1 of the legal text],
    [Your question related to aspect 2 of the legal text],
    ...
  ]
}
```

Ensure to replace the placeholders with actual analysis and questions based on the legal text provided, and in Vietnamese. Answer with the JSON and nothing else.

### Response:
"""
