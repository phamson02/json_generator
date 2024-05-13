import datetime
import json
import logging
import os
from collections.abc import Callable
from typing import Optional, TypeVar

from pydantic import ValidationError
from tenacity import RetryCallState, retry, stop_after_attempt
from tqdm import tqdm

from json_generator.data_module import InputModel, OutputModel

# Setup logging

log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)

run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"run_{run_id}.log"

logging.basicConfig(
    filename=os.path.join(log_dir, log_file),
    level=logging.INFO,
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
)

X = TypeVar("X", bound=InputModel)
Y = TypeVar("Y", bound=OutputModel)


def batch_completion_error_callback(
    retry_state: RetryCallState,
) -> OutputModel:
    logging.error(f"Error: {retry_state.outcome}")
    return retry_state.args[1].empty()


@retry(
    stop=stop_after_attempt(10),
    retry_error_callback=batch_completion_error_callback,
)
def retry_completion(
    input_model: InputModel,
    output_model: type[Y],
    generator: Callable[[list[str]], list[str]],
) -> Y:
    prompt = input_model.to_prompt()
    response = generator([prompt])
    output = output_model.model_validate_json(response[0])

    return output


def generate_batch(
    batch_inputs: list[X],
    output_model: type[Y],
    generator: Callable[[list[str]], list[str]],
) -> list[Y]:
    batch_user_prompts = [input_model.to_prompt() for input_model in batch_inputs]
    responses = generator(batch_user_prompts)

    outputs: list[Y] = []

    # for each response attempt to parse to output model
    # if parsing fails, retry the completion
    bad_response_indices: list[int] = []
    for i, response in enumerate(responses):
        try:
            output = output_model.model_validate_json(response)
            outputs.append(output)
        except ValidationError as e:
            logging.error(f"Failed to parse response: {e}")
            bad_response_indices.append(i)
            outputs.append(output_model.empty())

    for i in bad_response_indices:
        logging.warning(f"Bad response for prompt: {batch_user_prompts[i]}")
        outputs[i] = retry_completion(batch_inputs[i], output_model, generator)

    return outputs


def generate_and_save(
    *,
    inputs: list[X],
    output_model: type[Y],
    generator: Callable[[list[str]], list[str]],
    batch_size: int = 4,
    output_file: Optional[str] = None,
):
    batch_inputs = [
        inputs[i : i + batch_size] for i in range(0, len(inputs), batch_size)
    ]

    logging.info(f"Number of batches: {len(batch_inputs)}")

    output_file = output_file or f"outputs_{run_id}.jsonl"
    with open(output_file, "w") as f:
        for batch in tqdm(
            batch_inputs,
            total=len(batch_inputs),
            desc="Generating outputs for batch",
        ):
            outputs = generate_batch(batch, output_model, generator)

            for input_prompt, output in zip(batch, outputs):
                logging.info(
                    "Input: "
                    + input_prompt.model_dump_json(exclude={"input_prompt"}, indent=2)
                )
                logging.info(f"Output: {output.model_dump_json(indent=2)}")

                record = {
                    "input": input_prompt.model_dump(exclude={"input_prompt"}),
                    "output": output.model_dump(),
                }

                f.write(json.dumps(record, ensure_ascii=False) + "\n")

            f.flush()
