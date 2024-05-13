from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


def placeholder(name: str):
    return Field(..., serialization_alias=name)


class InputModel(ABC, BaseModel):
    input_prompt: str

    def to_prompt(self) -> str:
        """Replaces placeholders in the input_prompt with attribute values."""
        field_data = self.model_dump(by_alias=True)
        input_prompt = self.input_prompt
        for placeholder, actual_value in field_data.items():
            input_prompt = input_prompt.replace(placeholder, str(actual_value))
        return input_prompt


class OutputModel(ABC, BaseModel):

    @classmethod
    @abstractmethod
    def empty(cls) -> "OutputModel":
        pass
