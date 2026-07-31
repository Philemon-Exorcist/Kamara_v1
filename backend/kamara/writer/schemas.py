from dataclasses import dataclass
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class WriterSourceType(str, Enum):
    prompt = "prompt"
    image = "image"
    pdf = "pdf"
    text = "text"
    mixed = "mixed"


class WriterModuleSchema(BaseModel):
    sub_topic: str = Field(
        description="A crisp, topic-focused section title for the note package."
    )
    teaching_guidelines: str = Field(
        description="A compact section of note content, examples, formulas, and explanations."
    )


class WriterResponseSchema(BaseModel):
    title: str = Field(
        description="A human-friendly title for the generated study note package."
    )
    source_type: WriterSourceType = Field(
        description="Which input type(s) were used to generate the note package."
    )
    source_summary: str = Field(
        description="Short summary of the input source or attached material."
    )
    modules: list[WriterModuleSchema] = Field(
        description="An ordered list of 3 to 5 note sections.",
        min_length=3,
        max_length=5,
    )
    textbook_handout_notes: str = Field(
        description="A full Markdown study note that the tutor can later reuse.",
    )


class WriterRequestSchema(BaseModel):
    course: str = Field(description="The subject or course classification.")
    prompt: str = Field(description="The student prompt or learning objective.")
    helper_material_url: Optional[str] = Field(
        default=None,
        description="Optional public URL to a PDF, image, or text attachment.",
    )


@dataclass(slots=True)
class WriterContentBundle:
    source_type: WriterSourceType
    source_summary: str
    contents: list[object]
