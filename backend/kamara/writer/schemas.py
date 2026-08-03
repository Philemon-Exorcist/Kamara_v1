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
    section_notes: str = Field(
        description=(
            "The actual note content for this section, written like a textbook "
            "chapter: introduce the sub-topic, explain it clearly, note any "
            "important distinctions from related concepts, state relevant "
            "formulas/definitions, and include at least one fully worked "
            "example with the complete solution shown step by step. "
            "This must be pure subject-matter content. It must NEVER contain "
            "instructions about how to teach, present, pace, or explain the "
            "material (e.g. 'introduce this by...', 'draw a diagram showing...', "
            "'number each step') — that is the Tutor Agent's job, not yours. "
            "Every sentence here should be able to stand on its own as "
            "something you'd find printed in an actual textbook."
        )
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
        description="An ordered list of 3 to 5 note sections, arranged like chapters of a textbook.",
        min_length=3,
        max_length=5,
    )
    textbook_handout_notes: str = Field(
        description=(
            "The complete, assembled study note in clean Markdown — this is "
            "the single document the Tutor Agent will actually teach from. "
            "It should read like a well-edited textbook handout: headings, "
            "definitions, formulas, and fully worked examples with solutions. "
            "No teaching instructions here either — content only."
        ),
    )
    assessment_questions: list[str] = Field(
        description=(
            "3 to 6 practice questions drawn from this note's material, meant "
            "for the student to attempt at the end of the lesson. These must "
            "be left UNSOLVED — questions only, no answers or worked "
            "solutions — since they exist for the student to work out, not "
            "for you to answer. Make them related to, but not identical in "
            "wording to, the worked examples already included in the notes."
        ),
        min_length=3,
        max_length=6,
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