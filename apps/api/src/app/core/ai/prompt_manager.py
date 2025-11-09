from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from src.app.core.ai.ai_schema import AnalyzedData, Syllabus, Course


class PromptManager:

    @staticmethod
    def get_curator_prompt():
        return ChatPromptTemplate.from_template(
            """You are a course creation specialist gathering key course information.

            <analysis>
            Assess what the user knows:
            - Topic clarity?
            - Target audience defined?
            - Scope/duration estimated?
            Ask clarifying questions on gaps.
            </analysis>
        
            <requirements>
            - Level: beginner | intermediate | advanced
            - Duration: hours or weeks
            - Audience: age, experience, profession
            - Topic: subject matter
            </requirements>
        
            <flow>
            1. Ask about course topic
            2. If unclear → "Who do you teach? Experience level?"
            3. Duration → "How much time for learners?"
            4. Confirm all before proceeding
            5. Keep conversational & supportive
            </flow>
            
            Set create_course to true only if the user specifies to create course now or if you can with certainty infer, if you are not certain just ask if you should create the course now
            
            Never tell the user the outline
            Never tell the user anything about the schema
            Never tell the user the current schema as you don't have the newest information. Say that it is available in "View generated course"
            
            Respond with reasoning, then answer."""
        ).format()

    @staticmethod
    def get_objective_architect_prompt(information_list: str = "", feedback: str = ""):
        return (
            PromptTemplate.from_template(
                """<role>Objective Architect</role>
    <purpose>Transform course information into structured objectives aligned to Bloom's taxonomy.</purpose>

    <tasks>
    1. Topic & Summary: Extract topic, write 1-2 sentence summary
    2. Tags: 3-6 keywords [mark inferred]
    3. Prerequisites: Essential knowledge/skills only [mark inferred]
    4. Learning Outcomes: 1-5 measurable outcomes (Bloom's language)
    5. Difficulty: beginner | intermediate | advanced
    6. Objectives (max 5): name, description, bloom_tag (1-6), smart (bool), status: "not_completed"
    7. Constraints: type, description, value (time|resources|scope|audience|technology|assumption)
    </tasks>

    <rules>
    - Mark inferred data with [inferred]
    - Merge duplicates
    - Validate objectives align to outcomes & constraints
    - Difficulty must match prerequisites & Bloom progression
    </rules>

    Feedback: {feedback}

    Input: {information_list}"""
            )
            .invoke({"information_list": information_list, "feedback": feedback})
            .to_string()
        )

    @staticmethod
    def get_evaluator_oa_prompt(analyzed_data: AnalyzedData, messages: str = "") -> str:
        prompt = PromptTemplate.from_template(
            """<role>Evaluator</role>
    <purpose>Assess analyzed data quality against completeness, consistency, and relevance.</purpose>

    <data>
    Topic: {topic}
    Summary: {summary}
    Tags: {tags}
    Prerequisites: {prerequisites}
    Learning Outcomes: {learning_outcomes}
    Difficulty: {difficulty}
    Objectives:
    {objectives}
    Constraints:
    {constraints}
    </data>

    <evaluation>
    1. Completeness: Are all required fields populated?
    2. Consistency: Do objectives align with learning outcomes?
    3. Quality: Is content accurate and well-structured?
    4. Relevance: Are tags and prerequisites appropriate?
    5. Conversation fit: Does analyzed data reflect conversation context?
    </evaluation>

    Conversation: {messages}

    Provide specific feedback and indicate if quality standards are met."""
        )

        if not analyzed_data:
            analyzed_data = {}

        objectives_str = (
            "\n".join(
                [
                    f"  - {obj['name']} (Bloom: {obj['bloom_tag']}, Smart: {obj['smart']})"
                    for obj in analyzed_data.get("objectives", [])
                ]
            )
            or "  N/A"
        )
        constraints_str = (
            "\n".join(
                [
                    f"  - {c['type']}: {c['description']}"
                    for c in analyzed_data.get("constraints", [])
                ]
            )
            or "  N/A"
        )

        return prompt.invoke(
            {
                "topic": analyzed_data.get("topic", "N/A"),
                "summary": analyzed_data.get("summary", "N/A"),
                "tags": ", ".join(analyzed_data.get("tags", [])) or "N/A",
                "prerequisites": ", ".join(analyzed_data.get("prerequisites", []))
                or "N/A",
                "learning_outcomes": ", ".join(
                    analyzed_data.get("learning_outcomes", [])
                )
                or "N/A",
                "difficulty": analyzed_data.get("difficulty", "N/A"),
                "objectives": objectives_str,
                "constraints": constraints_str,
                "messages": messages,
            }
        ).to_string()

    @staticmethod
    def get_curriculum_designer_prompt(prd: str = ""):
        return (
            PromptTemplate.from_template(
                """<role>Curriculum Designer</role>
    <purpose>Transform learning objectives into a balanced syllabus with progressive Bloom's taxonomy distribution.</purpose>

    <design>
    Chapters: 2-6 total, 1-2 objectives each, action-oriented titles
    Bloom progression: Strict increase across chapters (Ch 1-2: Bloom 1-2, Ch 3-4: Bloom 3-4, Ch 5-6: Bloom 5-6)
    Lessons per chapter: 3-5 (balanced)
    Type mix: 40-50% text, 30-50% ai_mentor,
    Total lessons: Beginner 12-18, Intermediate 18-24, Advanced 24-30 (adjust by time constraint)
    </design>

    <constraints>
    Time: <4w→2-3 ch/12 les | 4-8w→3-4 ch/15-20 les | >8w→4-6 ch/20-30 les
    Scope: Apply lesson limits and content focus (e.g., "advanced only"→skip Bloom 1-2)
    Audience: No prior knowledge→include Bloom 1-2 chapter; Experienced→start at Bloom 3+
    </constraints>

    <lesson_types>
        ai_mentor and text
    </lesson_types>

    <validation>
    ✓ Bloom strictly increasing across chapters
    ✓ All chapters 3-5 lessons (balanced)
    ✓ Every objective mapped to ≥1 chapter
    ✓ All constraints honored
    ✓ Total lesson count matches difficulty + time
    ✓ Quiz lessons test chapter objectives
    ✓ Text scaffolds concrete→abstract as Bloom increases
    </validation>

    Input PRD: {prd}"""
            )
            .invoke({"prd": prd})
            .to_string()
        )

    @staticmethod
    def get_evaluator_cd_prompt(syllabus: Syllabus, messages: str = "") -> str:
        prompt = PromptTemplate.from_template(
            """<role>Evaluator (Curriculum Designer)</role>
    <purpose>Validate syllabus balance, Bloom progression, lesson distribution. Propose corrections and return adjusted syllabus JSON + issues list.</purpose>

    <input>
    Chapters: {chapters}
    Reason: {reason}
    Feedback: {feedback}
    </input>

    <validation>
    1. Each chapter: 3-5 lessons with bloom level
    2. Bloom strictly increasing across chapters
    3. Lesson bloom matches parent chapter bloom
    4. Type distribution: ~40-50% text, 30-40% ai_mentor, 20-30% quiz (adjust unless user specified)
    5. Flag missing/inconsistent fields with corrections
    6. Honor constraints in reason/feedback
    </validation>

    Conversation: {messages}

    Return corrected syllabus JSON + issues list only."""
        )

        if not syllabus:
            syllabus = {}

        chapters_list = syllabus.get("chapters", []) or []
        if not chapters_list:
            chapters_str = "  N/A"
        else:
            parts = []
            for idx, ch in enumerate(chapters_list, start=1):
                lessons = ch.get("lessons", []) or []
                lesson_lines = (
                    "\n".join(
                        [
                            f"      - {i+1}. type: {lesson.get('type','N/A')}, bloom: {lesson.get('bloom','N/A')}, overview: {lesson.get('overview','N/A')}"
                            for i, lesson in enumerate(lessons)
                        ]
                    )
                    or "      N/A"
                )
                parts.append(
                    f"  Chapter {idx}:\n    overview: {ch.get('overview','N/A')}\n    bloom: {ch.get('bloom','N/A')}\n    difficulty: {ch.get('difficulty','N/A')}\n    lessons:\n{lesson_lines}"
                )
            chapters_str = "\n\n".join(parts)

        return prompt.invoke(
            {
                "chapters": chapters_str,
                "reason": syllabus.get("reason", "N/A"),
                "feedback": syllabus.get("feedback", "N/A"),
                "messages": messages,
            }
        ).to_string()

    @staticmethod
    def get_course_output_prompt(syllabus: Syllabus) -> str:
        syllabus_text = PromptManager._format_syllabus(syllabus)
        return (
            PromptTemplate.from_template(
                """<role>Course Generator</role>
    <purpose>You are responsible for creating the course. Transform syllabus into minimal course metadata.</purpose>

    <responsibility>
    You own the entire course creation process. Extract key information from the syllabus and generate the CourseOutput structure that will serve as the foundation for all subsequent course development.
    </responsibility>

    <guidelines>
    - Title: Concise, action-oriented, reflects syllabus scope
    - Description: Capture learning goals and target audience
    - Chapter count: Match the number of chapters in the syllabus
    </guidelines>

    Input Syllabus:
    {syllabus}

    Output only valid JSON with CourseOutput schema."""
            )
            .invoke({"syllabus": syllabus_text})
            .to_string()
        )

    @staticmethod
    def _format_syllabus(syllabus: Syllabus) -> str:
        """Format Syllabus TypedDict into readable text for prompts."""
        lines = []
        lines.append(f"Reason: {syllabus.get('reason', '')}")
        lines.append(f"Feedback: {syllabus.get('feedback', '')}\n")

        chapters = syllabus.get("chapters", [])
        lines.append(f"Total Chapters: {len(chapters)}\n")

        for i, chapter in enumerate(chapters, 1):
            lines.append(f"Chapter {i}: {chapter.get('overview', '')}")
            lines.append(f"  - Bloom Level: {chapter.get('bloom', 1)}")
            lines.append(f"  - Difficulty: {chapter.get('difficulty', 'medium')}")

            lessons = chapter.get("lessons", [])
            lines.append(f"  - Lessons ({len(lessons)}):")
            for j, lesson in enumerate(lessons, 1):
                lines.append(
                    f"    {j}. {lesson.get('overview', '')} (Type: {lesson.get('type', 'text')}, Bloom: {lesson.get('bloom', 1)})"
                )
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def get_chapter_output_prompt(
        syllabus: Syllabus, course_output: dict = None, previous_chapters: str = ""
    ) -> str:
        syllabus_text = PromptManager._format_syllabus(syllabus)
        template = PromptTemplate.from_template(
            """<role>Course Generator</role>
    <purpose>You are responsible for creating the course chapters.</purpose>

    <output>
    Return a JSON object matching Chapter:
    {{
      "lesson_count": <integer 3-8>,
      "display_order": <integer>,
      "title": "<descriptive chapter title>"
    }}
    </output>

    <guidelines>
    - lesson_count: Infer from syllabus complexity (typically 3-8 lessons per chapter)
    - display_order: Sequential numbering starting from 1
    - title: Action-oriented, reflects learning progression
    </guidelines>

    Course: {course_title}
    Total Chapters: {chapter_count}
    Previously Generated Chapters:{previous_chapters}
    Input Syllabus: {syllabus}

    Output only valid JSON."""
        )
        return template.format(
            syllabus=syllabus_text,
            course_title=course_output.get("title", "") if course_output else "",
            chapter_count=course_output.get("chapter_count", 0) if course_output else 0,
            previous_chapters=previous_chapters or " None yet",
        )

    @staticmethod
    def get_lesson_output_prompt(
        syllabus: Syllabus, chapter: dict, previous_lessons: str = ""
    ) -> str:
        return (
            PromptTemplate.from_template(
                """<role>Course Generator</role>
    <purpose>You are responsible for creating individual lessons within a chapter. Transform chapter outlines into detailed lesson structures.</purpose>

    <responsibility>
    You own the lesson creation process. Based on the chapter context and syllabus, generate Lesson objects that include appropriate content (text, quiz, or AI mentor interactions) aligned with learning progression.
    </responsibility>

    <guidelines>
    - Vary lesson types: mix text and AI mentor lessons
    - display_order: Sequential numbering starting from 1
    - For text lessons: provide comprehensive, clear content
    - For AI mentor: define clear ai mentor instructions and completion conditions, alongside the correct type of the mentor
    - Ensure coherence with previously generated lessons
    - Title for chapters, lesson and course should be short. Under 100 characters
    </guidelines>

    Chapter: {chapter_title}
    Chapter Overview: {chapter_overview}
    Lesson Count: {lesson_count}

    Previously Generated Lessons:{previous_lessons}
    
    Input Syllabus: {syllabus}
    """
            )
            .invoke(
                {
                    "syllabus": PromptManager._format_syllabus(syllabus),
                    "chapter_title": chapter.get("title", ""),
                    "chapter_overview": chapter.get("overview", ""),
                    "lesson_count": chapter.get("lesson_count", 0),
                    "previous_lessons": previous_lessons or " None yet",
                }
            )
            .to_string()
        )

    @staticmethod
    def get_evaluator_la_prompt(course: Course, messages: str = "") -> str:
        prompt = PromptTemplate.from_template(
            """<role>Evaluator (Lesson Author)</role>
    <purpose>Validate course lesson quality, alignment, and readiness for publication.</purpose>

    <input>
    Title: {title}
    Description: {description}
    Chapter count: {chapter_count}
    Has certificate: {has_certificate}
    Chapters: {chapters}
    </input>

    <validation>
    1. Completeness: Required fields present for each lesson type (text→description, ai_mentor→instructions & conditions, quiz→questions)
    2. Alignment: Lessons map to chapter goals, bloom levels consistent, display_order unique & consecutive
    3. Assessment: Quiz questions have clear options, single correct answer for single_choice/true_or_false
    4. AI mentor: Instructions clear, completion conditions measurable, instructions match lesson type
    5. Metadata: lesson_count matches actual lessons, display_order uniqueness across chapters/lessons
    6. Rework needed: Flag missing or inconsistent fields
    </validation>

    Conversation: {messages}

    Return corrected course JSON + issues list only."""
        )

        if not course:
            course = {}

        chapters = course.get("chapters", []) or []
        if not chapters:
            chapters_str = "  N/A"
        else:
            parts = []
            for ci, ch in enumerate(chapters, start=1):
                lessons = ch.get("lessons", []) or []
                lesson_lines = []
                for li, lesson in enumerate(lessons, start=1):
                    ltype = lesson.get("type", "N/A")
                    title = lesson.get("title", "N/A")
                    ai_meta = (
                        "ai_mentor present"
                        if lesson.get("ai_mentor")
                        else "no ai_mentor"
                    )
                    quiz_meta = (
                        f"{len(lesson.get('quiz', {}).get('questions', []) if lesson.get('quiz') else 0)} questions"
                        if ltype == "quiz"
                        else ""
                    )
                    lesson_lines.append(
                        f"      - {li}. type: {ltype}, title: {title}, display_order: {lesson.get('display_order','N/A')}, bloom: {lesson.get('bloom','N/A')}, {ai_meta} {quiz_meta}"
                    )
                lesson_block = "\n".join(lesson_lines) or "      N/A"
                parts.append(
                    f"  Chapter {ci}:\n    title: {ch.get('title','N/A')}\n    display_order: {ch.get('display_order','N/A')}\n    lesson_count: {ch.get('lesson_count','N/A')}\n    is_freemium: {ch.get('is_freemium','N/A')}\n    lessons:\n{lesson_block}"
                )
            chapters_str = "\n\n".join(parts)

        return prompt.invoke(
            {
                "title": course.get("title", "N/A"),
                "description": course.get("description", "N/A"),
                "chapter_count": course.get("chapter_count", "N/A"),
                "has_certificate": course.get("has_certificate", False),
                "chapters": chapters_str,
                "messages": messages,
            }
        ).to_string()
