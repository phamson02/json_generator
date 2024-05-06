import datetime
import json
import logging
import os
from collections.abc import Callable
from typing import Optional

from tenacity import retry, stop_after_attempt
from tqdm import tqdm

from .input_prompt import input_prompt
from .utils import escape_json_string

# Setup logging

log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)

run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"queries_gen_claude_{run_id}.log"

logging.basicConfig(
    filename=os.path.join(log_dir, log_file),
    level=logging.INFO,
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class Content:
    def __init__(self, domain: str, metadata: str, grounded_content: str):
        self.domain = domain
        self.metadata = metadata
        self.grounded_content = grounded_content

    # f"DOC_DOMAIN: {self.domain}\nDOC_SOURCE: {self.metadata}\nDOC_GROUNDED_CONTENT: {self.grounded_content}"
    def __str__(self) -> str:
        return f"DOC_DOMAIN: {self.domain}\nDOC_SOURCE: {self.metadata}\nDOC_GROUNDED_CONTENT: {self.grounded_content}"

    def __repr__(self) -> str:
        return f"""Content(\n\tDOC_DOMAIN: {self.domain},\n\tDOC_SOURCE: {self.metadata},\n\tDOC_GROUNDED_CONTENT: {self.grounded_content}\n)"""

    @staticmethod
    def from_list(
        domain_list: list[str],
        metadata_list: list[str],
        grounded_content_list: list[str],
    ) -> list["Content"]:
        assert (
            len(domain_list) == len(metadata_list) == len(grounded_content_list)
        ), "Mismatched lengths of input lists"

        return [
            Content(domain, metadata, grounded_content)
            for domain, metadata, grounded_content in zip(
                domain_list, metadata_list, grounded_content_list
            )
        ]

    def to_user_message(self) -> str:
        # Dictionary of placeholders and their corresponding values
        replacements = {
            "{$DOC_DOMAIN}": self.domain,
            "{$DOC_SOURCE}": self.metadata,
            "{$DOC_GROUNDED_CONTENT}": self.grounded_content,
        }

        # Start with the original system prompt
        user_message = input_prompt

        # Replace each placeholder with its corresponding value
        for placeholder, actual_value in replacements.items():
            user_message = user_message.replace(placeholder, actual_value)

        return user_message


def batch_completion_error_callback(
    retry_state,
) -> tuple[list[str], list[str]]:
    logging.error(f"Error: {retry_state.outcome}")
    return [], []


@retry(
    stop=stop_after_attempt(10),
    retry_error_callback=batch_completion_error_callback,
)
def retry_completion(
    content: Content,
    generator: Callable[[list[str]], list[str]],
) -> tuple[list[str], list[str]]:
    prompt = content.to_user_message()
    response = generator([prompt])
    aspects, questions = get_questions_from_message(response[0])

    return aspects, questions


def generate_batch(
    batch_contents: list[Content],
    generator: Callable[[list[str]], list[str]],
) -> tuple[list[list[str]], list[list[str]]]:
    contents = [content.to_user_message() for content in batch_contents]

    responses = generator(contents)

    batch_aspects, batch_questions = get_questions_from_batch(responses)

    bad_response_indices = [
        len(aspect) == 0 or len(question) == 0
        for aspect, question in zip(batch_aspects, batch_questions)
    ]

    if any(bad_response_indices):
        for i, bad_response in enumerate(bad_response_indices):
            if bad_response:
                logging.warning(f"Bad response for content: {batch_contents[i]}")

                aspects, questions = retry_completion(batch_contents[i], generator)

                batch_aspects[i] = aspects
                batch_questions[i] = questions

    return batch_aspects, batch_questions


def get_questions_from_message(message: str) -> tuple[list[str], list[str]]:
    try:
        parsed = json.loads(message)
    except json.JSONDecodeError:
        logging.warning(f"Trying to escape JSON string in message: {message}")
        message = escape_json_string(message)
        try:
            parsed = json.loads(message)
        except json.JSONDecodeError as e:
            logging.error(f"Attempted to escape JSON string, but still failed: {e}")
            return [], []

    aspects = parsed.get("aspects")
    questions = parsed.get("questions")

    if aspects is None or questions is None:
        logging.error(f"Missing 'aspects' or 'questions' in JSON: {message}")
        return [], []

    return aspects, questions


def get_questions_from_batch(
    messages: list[str],
) -> tuple[list[list[str]], list[list[str]]]:
    aspects_list = []
    questions_list = []
    for message in messages:
        aspects, questions = get_questions_from_message(message)
        aspects_list.append(aspects)
        questions_list.append(questions)

    return aspects_list, questions_list


def generate_and_save_queries(
    contents: list[Content],
    generator: Callable[[list[str]], list[str]],
    batch_size: int = 4,
    output_file: Optional[str] = None,
):
    # Split contents into batches
    batch_contents = [
        contents[i : i + batch_size] for i in range(0, len(contents), batch_size)
    ]

    logging.info(f"Number of batches: {len(batch_contents)}")

    output_file = output_file or f"questions_{run_id}.jsonl"
    with open(output_file, "w") as f:
        for batch_index, batch in tqdm(
            enumerate(batch_contents),
            total=len(batch_contents),
            desc="Generating queries for batch",
        ):
            batch_aspects, batch_questions = generate_batch(batch, generator)

            for content_index, (aspects, questions) in enumerate(
                zip(batch_aspects, batch_questions)
            ):
                content_id = batch_index * batch_size + content_index
                json_record = json.dumps(
                    {"id": content_id, "aspects": aspects, "queries": questions},
                    indent=4,
                    ensure_ascii=False,
                )

                f.write(json_record + "\n")

                f.flush()

                logging.info(f"Content {content_id}: {contents[content_id]}")

                for j, (aspect, question) in enumerate(zip(aspects, questions)):
                    logging.info(f"{j + 1}. {aspect}")
                    logging.info(f"{j + 1}. {question}")
