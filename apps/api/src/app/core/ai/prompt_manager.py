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
        
            Respond with reasoning, then answer."""
        )

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
    Type mix: 40-50% text, 30-40% ai_mentor, 20-30% quiz
    Total lessons: Beginner 12-18, Intermediate 18-24, Advanced 24-30 (adjust by time constraint)
    </design>

    <constraints>
    Time: <4w→2-3 ch/12 les | 4-8w→3-4 ch/15-20 les | >8w→4-6 ch/20-30 les
    Scope: Apply lesson limits and content focus (e.g., "advanced only"→skip Bloom 1-2)
    Audience: No prior knowledge→include Bloom 1-2 chapter; Experienced→start at Bloom 3+
    Technology: No interactives→reduce ai_mentor, increase quizzes
    </constraints>

    <lesson_types>
    Bloom 1-2: true_or_false, single_choice, text
    Bloom 3-4: multiple_choice, brief_response, single_choice
    Bloom 5-6: detailed_response, multiple_choice (complex scenarios), ai_mentor
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
    def get_lesson_author_prompt(syllabus: str = ""):
        return (
            PromptTemplate.from_template(
                """<role>Lesson Author</role>
    <purpose>Convert lesson outlines into fully-authored content aligned to Bloom's taxonomy and learning objectives.</purpose>

    <content_types>
    Text lessons: 200-1000 words | Include hook, 3-5 sections, worked example, key takeaways, practice prompt
    AI mentor: Scenario setup, initial prompt, tiered hints, correct path, extension, completion criteria
    Quiz: 2-6 questions with context, options, correct answer, explanations, rubric for detailed-response
    </content_types>

    <bloom_mapping>
    Bloom 1-2 (Remember/Understand):
    - Text: Definitions, diagrams, basic explanations (200-400w, clear/direct language)
    - AI: Leading questions, recall hints (e.g., "What's the first step? (Hint: involves...)")
    - Quiz: True/False, single-choice (3-5 questions, one concept each)

    Bloom 3-4 (Apply/Analyze):
    - Text: Scenarios, case studies, comparisons (400-700w, analytical language)
    - AI: Apply concepts to scenarios, corrective feedback (e.g., "Which method for this dataset?")
    - Quiz: Multiple-choice complex stems, brief-response (4-6 questions, misconception distractors)

    Bloom 5-6 (Evaluate/Create):
    - Text: Complex scenarios, design challenges (600-1000w, evaluative/conditional language)
    - AI: Real-world dilemmas, challenge reasoning (e.g., "Design with X/Y trade-offs")
    - Quiz: Detailed-response with rubric (2-4 questions, scenario-based)
    </bloom_mapping>

    <guidelines>
    - Concreteness: Real-world examples early → abstract/theoretical later
    - Progression: Examples go concrete → abstract; Bloom increases across chapters
    - Accessibility: Plain language, 15-20 word sentences, active voice, jargon defined
    - Assessment: Quiz questions test specific lesson objectives, match Bloom levels
    - AI mentor: Provide scaffolding without giving answers; include measurable completion criteria
    - Worked examples: Bloom 3-4 include step-by-step solutions; Bloom 4-5 show contrasts (what works/doesn't)
    </guidelines>

    <output>
    Course object:
    - title, description (2-3 sentences)
    - chapters: [title, display_order, is_freemium (true for ch 1), lessons]
    - lessons: [type, title, description (full content), display_order, ai_mentor (if type=ai_mentor), quiz (if type=quiz)]
    - reason (2-3 sentences)
    - feedback (clarity, Bloom alignment, assessment quality)
    </output>

    <validation>
    ✓ Content reflects Bloom level (language, complexity, examples)
    ✓ Quiz questions match Bloom levels
    ✓ Examples progress concrete → abstract
    ✓ AI mentor scaffolds appropriately
    ✓ All learning outcomes addressed
    ✓ Assessment aligned to objectives
    ✓ Language clear, jargon defined, examples inclusive
    </validation>

    Input Syllabus: {syllabus}"""
            )
            .invoke({"syllabus": syllabus})
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
