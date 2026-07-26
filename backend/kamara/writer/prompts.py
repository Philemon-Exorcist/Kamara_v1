from pathlib import Path


CURRENT_DIR = Path(__file__).parent
SKILLS_FILE_PATH = CURRENT_DIR / "writer_skills" / "research_skill.md"


def _load_skill_block() -> str:
    try:
        return SKILLS_FILE_PATH.read_text(encoding="utf-8")
    except Exception:
        return "Apply advanced curriculum writing and markdown skills."


def build_writer_system_prompt() -> str:
    skill_block = _load_skill_block()
    return (
        "You are Kamara AI's primary Curriculum Designer and Textbook Writer.\n"
        "Your job is to read a student prompt, and when present, read attached PDFs or images, "
        "then compile a structured study note package that can be saved for later tutoring.\n\n"
        "You must return rigorous, board-friendly, tutor-ready study material.\n\n"
        "=========================================\n"
        f"{skill_block}\n"
        "=========================================\n"
    )


def build_writer_user_prompt(course: str, prompt: str, source_type: str, source_summary: str) -> str:
    return (
        f"Course Subject Classification: {course}\n"
        f"Student Main Learning Goal: {prompt}\n"
        f"Source Type: {source_type}\n"
        f"Source Summary: {source_summary}\n\n"
        "OUTPUT REQUIREMENT:\n"
        "Return a structured note package that matches the JSON schema exactly.\n"
        "The note package should be detailed enough for a tutoring agent to reuse directly.\n"
        "Include 3 to 5 lesson modules, each with teaching guidance for the whiteboard.\n"
        "Write the final note in clean Markdown with headings, bullets, and concise explanations.\n"
    )
