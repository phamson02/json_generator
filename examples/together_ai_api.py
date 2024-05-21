import asyncio
import random

import aiohttp
import aiolimiter
from pydantic import BaseModel

from legal_queries_generator import (
    InputModel,
    OutputModel,
    generate_and_save,
    placeholder,
)

passage_generation_prompt = """Your task is to generate two passages in Vietnamese for the given legal query - a positive passage that comprehensively answers the query, and a "hard negative" passage that may seem relevant at first glance but is actually less useful in addressing the query.

Here is the legal query:
<legal_query>
{{LEGAL_QUERY}}
</legal_query>

The query is in this domain: 
<domain>{{DOMAIN}}</domain>

A "hard negative" passage has these key characteristics:
- It is on the same general topic as the query 
- It mentions some keywords and phrases from the query to seem relevant
- However, it does not actually answer the query as directly or thoroughly as a good positive passage would
- It may leave out key information, be vaguer/broader in scope, or focus more on tangential details
- Overall, a user should clearly find a positive passage more helpful than the hard negative in addressing their query, even if the hard negative initially seems promising

The content of both passages should be no more than 400 words.

Here is an example of a suitable positive passage and hard negative passage for the query "Bộ Giao thông vận tải giải thích như thế nào về các từ ngữ như 'hệ thống thông tin' và 'dữ liệu' trong quy định về thiết bị giám sát hành trình?":
<positive_passage_example>
<domain>Giao thông - Vận tải</domain>
<source>Thông tư 09/2015/TT-BGTVT Quy định về cung cấp, quản lý và sử dụng dữ liệu từ thiết bị giám sát hành trình của xe ô tô do Bộ Giao thông vận tải ban hành.</source>
<content>Chương I. QUY ĐỊNH CHUNG
Điều 1. Phạm vi điều chỉnh. Thông tư này quy định về cung cấp, quản lý và sử dụng dữ liệu từ thiết bị giám sát hành trình của xe ô tô sau (sau đây gọi chung là thiết bị giám sát hành trình).
Điều 2. Đối tượng áp dụng. Thông tư này áp dụng đối với các đơn vị kinh doanh vận tải, bến xe khách, bến xe hàng, các đơn vị cung cấp dịch vụ giám sát hành trình và các cơ quan, tổ chức, cá nhân có liên quan đến việc cung cấp, quản lý và sử dụng dữ liệu từ thiết bị giám sát hành trình của xe ô tô trong phạm vi toàn quốc.
Điều 3. Giải thích từ ngữ. Trong Thông tư này, các từ ngữ dưới đây được hiểu như sau:
1. Hệ thống thông tin: là tập hợp các thiết bị phần cứng, phần mềm và đường truyền dùng để thu nhận, quản lý, khai thác dữ liệu từ thiết bị giám sát hành trình.
2. Dữ liệu: là tập hợp các thông tin có cấu trúc được truyền từ thiết bị giám sát hành trình về máy chủ dịch vụ và từ máy chủ dịch vụ truyền về Tổng cục Đường bộ Việt Nam.</content>
</positive_passage_example>
<hard_negative_example>
<domain>Công nghệ thông tin</domain>
<source>Nghị định 64/2007/NĐ-CP về ứng dụng công nghệ thông tin trong hoạt động của cơ quan nhà nước, Chương II</source>
</content>Điều 6. Nguyên tắc xây dựng, quản lý và sử dụng hệ thống thông tin
1. Hệ thống thông tin phải đáp ứng yêu cầu công việc, phù hợp với điều kiện thực tế của cơ quan, tổ chức và được cập nhật, nâng cấp thường xuyên.
2. Việc xây dựng, quản lý và sử dụng hệ thống thông tin phải bảo đảm an toàn, an ninh thông tin; thống nhất, đồng bộ, tránh chồng chéo, lãng phí.
3. Dữ liệu trong hệ thống thông tin phải được bảo đảm tính chính xác, đầy đủ, kịp thời và được sao lưu, lưu trữ an toàn.
4. Việc khai thác, sử dụng dữ liệu trong hệ thống thông tin phải bảo đảm tính hợp pháp, đúng mục đích và có biện pháp bảo vệ thông tin cá nhân</content>
</hard_negative_example>

Please generate your positive and hard negative passages and format them in JSON like this:

<format>
{
  "positive": {
    "domain": [domain of positive passage],
    "source": [source of positive passage],
    "content": [content of positive passage]
  },
  "hard_negative": {
    "domain": [domain of hard negative passage],  
    "source": [source of hard negative passage],
    "content": [content of hard negative passage]
  }
}
</format>

Fill in the actual details for [domain], [source], and [content] for each passage. The domain and source should be distinct between the two passages. The content should be in Vietnamese and directly relevant to the provided legal query and domain.

Provide only the JSON output, with no other text. Make sure the JSON is properly formatted."""


class LegalQuery(InputModel):
    input_prompt: str = passage_generation_prompt
    query: str = placeholder("{{LEGAL_QUERY}}")
    domain: str = placeholder("{{DOMAIN}}")

    def __repr__(self) -> str:
        return f"LegalQuery(query={self.query}, domain={self.domain})"


class LegalPassage(BaseModel):
    domain: str = ""
    source: str = ""
    content: str = ""


class LegalPassagePair(OutputModel):
    positive: LegalPassage
    hard_negative: LegalPassage

    @classmethod
    def empty(cls) -> "LegalPassagePair":
        return cls(positive=LegalPassage(), hard_negative=LegalPassage())


async def together(text: str, api_key: str) -> str:
    endpoint = "https://api.together.xyz/v1/chat/completions"
    connector = aiohttp.TCPConnector(
        force_close=True, limit=10
    )  # To avoid ServerDisconnectedError
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.post(
            endpoint,
            json={
                "model": "meta-llama/Llama-3-70b-chat-hf",
                "max_tokens": 1200,
                "temperature": 0.4,
                "top_p": 0.7,
                "top_k": 50,
                "repetition_penalty": 1,
                "stop": ["<|eot_id|>"],
                "messages": [
                    {
                        "content": text,
                        "role": "user",
                    }
                ],
            },
            headers={
                "Authorization": f"Bearer {api_key}",
            },
        ) as res:
            if res.status != 200:
                print(f"Failed to generate query: {res.status}")
                return ""

            try:
                data = await res.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"Failed to generate query: {e}")
                return ""


def generator(contents: list[str]) -> list[str]:
    with open("together_api_keys.txt") as f:
        api_keys = f.read().splitlines()

    generated_contents: list[str] = []

    # rotating api keys
    def api_key_pool():
        while True:
            for api_key in api_keys:
                yield api_key

    limiter = aiolimiter.AsyncLimiter(len(api_keys), 1)

    async def fetch(content, api_key):
        async with limiter:
            return await together(content, api_key)

    async def async_generate():
        # For some low probability, take a break of 5 seconds
        take_a_break = random.random() < 0.01
        if take_a_break:
            print("Taking a 5 seconds break, hold on...")
            await asyncio.sleep(5)

        tasks: list[asyncio.Task[str]] = []
        for content, api_key in zip(contents, api_key_pool()):
            tasks.append(asyncio.create_task(fetch(content, api_key)))

        generated_contents.extend(await asyncio.gather(*tasks))

    asyncio.run(async_generate())

    return generated_contents


if __name__ == "__main__":
    queries: list[str] = [
        "Bộ Giao thông vận tải giải thích như thế nào về các từ ngữ như 'hệ thống thông tin' và 'dữ liệu' trong quy định về thiết bị giám sát hành trình?",
        "Nếu một người lái xe không đeo dây an toàn, cảnh sát có quyền xử phạt ngay tại chỗ không?",
    ]
    domains: list[str] = [
        "Giao thông - Vận tải",
        "Pháp luật",
    ]

    inputs = [
        LegalQuery(
            query=query,
            domain=domain,
        )
        for query, domain in zip(queries, domains)
    ]

    print(f"Number of queries: {len(inputs)}")

    generate_and_save(
        inputs=inputs,
        output_model=LegalPassagePair,
        batch_size=4,
        generator=generator,
    )
