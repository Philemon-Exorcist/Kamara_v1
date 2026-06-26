



import json
import logging
import os
import re
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field

# Core Google GenAI SDK Client & Model Elements
from google import genai
from google.genai import types
from dotenv import load_dotenv



# environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("Gemini Api Key Missing")


#

logger = logging.getLogger("KamaraLogger")
# Lock to a supported model so older environment values cannot force 404s.
WRITER_MODEL = "gemini-2.5-flash"

# =====================================================================
# STRUCTURAL PYDANTIC DATA SCHEMAS FOR DATABASE INSERTION
# =====================================================================
class ModuleStepSchema(BaseModel):
    sub_topic: str = Field(description="The crisp name of the subtopic section, e.g., 'Matrix Inverses'")
    teaching_guidelines: str = Field(description="Visual whiteboard goals, matrix structures, and content layouts to guide the session.")


class SyllabusResponseSchema(BaseModel):
    modules: List[ModuleStepSchema] = Field(description="An ordered sequential list of exactly 3 to 5 learning subtopics.")
    textbook_handout_notes: str = Field(description="The entire compiled, long-form textbook study guide formatted in rich Markdown.")


# =====================================================================
# DYNAMIC SKILLSET LOADER ROUTINE
# =====================================================================
CURRENT_DIR = Path(__file__).parent
SKILLS_FILE_PATH = CURRENT_DIR / "writer_skills" / "research_skill.md"

try:
    with open(SKILLS_FILE_PATH, "r", encoding="utf-8") as file:
        skills_instruction_block = file.read()
except Exception as e:
    skills_instruction_block = "Apply advanced curriculum writing and markdown skills."


# Declare your tools directly as functions in the GenerateContentConfig array.
# The core SDK reads their Python typings and docstrings automatically.
#from .writer_tools.research import google_search_curriculum, fetch_academic_benchmarks
#WRITER_TOOLS = [google_search_curriculum, fetch_academic_benchmarks]


MASTER_WRITER_INSTRUCTION = (
    "You are Kamara AI's primary Curriculum Designer and Textbook Writer. Your job is to take a topic "
    "and subject, execute deep academic research using your tools, and compile a structured module roadmap "
    "alongside an extensive textbook handout guide. You never speak to the student live.\n\n"
    "=========================================\n"
    f"{skills_instruction_block}\n"
    "=========================================\n\n"
    "OUTPUT REQUIREMENT:\n"
    "Synthesize all facts and compile your final output to match the requested SyllabusResponseSchema structure perfectly."
)


# =====================================================================
# CONTEXT PARSING & STATIC FALLBACK RULES
# =====================================================================
def _extract_course_context(message: str) -> tuple[str, str]:
    subject_match = re.search(r"Course Subject Classification:\s*(.+)", message)
    goal_match = re.search(r"Student Main Learning Goal:\s*(.+)", message)

    subject = subject_match.group(1).strip() if subject_match else "General Studies"
    goal = goal_match.group(1).strip() if goal_match else "the requested topic"
    return subject or "General Studies", goal or "the requested topic"


def _fallback_syllabus(message: str) -> SyllabusResponseSchema:
    subject, goal = _extract_course_context(message)
    topic = goal[:90].strip(". ") or subject

    modules = [
        ModuleStepSchema(
            sub_topic=f"{subject.title()} foundations",
            teaching_guidelines=(
                f"Introduce the key vocabulary behind {topic}. On the board, place the main idea in the center, "
                "draw three labeled branches for definitions, assumptions, and common mistakes, then add one "
                "short worked example beside each branch."
            ),
        ),
        ModuleStepSchema(
            sub_topic="Core methods and worked examples",
            teaching_guidelines=(
                "Build two side-by-side examples: one basic case and one exam-style case. Number every step, "
                "circle each formula or rule when it first appears, and end with a short checkpoint question."
            ),
        ),
        ModuleStepSchema(
            sub_topic="Practice pathway and mastery checks",
            teaching_guidelines=(
                "Create a three-level practice ladder labeled warm-up, standard, and challenge. For each level, "
                "show the expected first move, the reasoning cue, and the final answer-check habit."
            ),
        ),
    ]

    notes = (
        f"# Study Guide: {subject.title()}\n\n"
        f"## Learning Goal\n{goal}\n\n"
        "## How To Study This Topic\n"
        "Start with the definitions, then work through guided examples before attempting independent practice. "
        "After each example, explain why the method works in your own words.\n\n"
        "## Core Roadmap\n"
        "1. Identify the key terms and what each one means.\n"
        "2. Learn the standard method or rule set.\n"
        "3. Apply the method to simple examples.\n"
        "4. Increase difficulty with mixed practice.\n"
        "5. Review mistakes and rewrite the correct reasoning.\n\n"
        "> **Concept Check:** You understand the topic when you can solve a fresh problem and explain each step "
        "without copying the example.\n\n"
        "## Practice Routine\n"
        "- Complete three warm-up questions.\n"
        "- Complete two standard questions without notes.\n"
        "- Write one summary paragraph explaining the method.\n"
    )

    return SyllabusResponseSchema(modules=modules, textbook_handout_notes=notes)


# =====================================================================
# CORE SDK HIGH-PERFORMANCE ROUTINE RUNNER
# =====================================================================
async def run_syllabus_designer(message: str, user_id: str = "course-generator") -> SyllabusResponseSchema:
    """
    Agent 2 (The Writer Agent): Compiles structured syllabus plans and markdown textbook 
    handout data files out-of-band using the type-safe core google-genai SDK framework.
    """

    client = genai.Client(api_key=api_key)

    # 2. Package your structural content configuration payload rules
    config = types.GenerateContentConfig(
        system_instruction=MASTER_WRITER_INSTRUCTION,
        temperature=0.2,               # Low temperature guarantees analytical, non-hallucinated curriculum data
        response_mime_type="application/json",
        response_schema=SyllabusResponseSchema,  # NATIVE server-level structural enforcement hook
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )

    try:
        logger.info(f"🧬 Initializing core GenAI Writer Engine for designer instance: {user_id}")
        logger.info("Writer model selected: %s", WRITER_MODEL)
        
        # 3. Request structural generation directly from the asynchronous client wrapper layer
        response = await client.aio.models.generate_content(
            model=WRITER_MODEL,
            contents=message,
            config=config
        )

        if not response.text:
            raise ValueError("Google GenAI client returned a null or empty text payload response string.")

        # 4. Safely parse verified raw JSON structures directly back into your destination target schema
        return SyllabusResponseSchema.model_validate_json(response.text)

    except Exception as e:
        logger.error("Core Google GenAI SDK Writer failed; rolling over to local static fallback definitions: %s", str(e), exc_info=True)
        return _fallback_syllabus(message)
    finally:
        logger.info("Writer engine finished for designer instance: %s", user_id)
