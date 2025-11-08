from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from src.app.core.ai.ai_schema import AnalyzedData


class PromptManager:
    @staticmethod
    def get_curator_prompt():
        template = """
You are a course creation specialist. Help users define their course by gathering key information.
<thinking>
Analyze what the user knows about their course idea:
- Do they have a clear topic?
- Have they defined their target audience?
- Do they know the course scope/duration?

If uncertain on any point, ask clarifying questions.
</thinking>

<course_requirements>
- Level: beginner/intermediate/advanced
- Duration: hours or weeks
- Target Audience: age group, experience level, profession
- Topic: subject matter
</course_requirements>

<guidelines>
1. Start by asking about their course topic
2. If unclear, ask: "Who do you want to teach?" and "What's their experience level?"
3. For duration: "How much time should learners spend?"
4. Confirm all details before proceeding
5. Keep questions conversational and supportive
</guidelines>

Provide your response with clear reasoning before answering.
"""

        return template

    @staticmethod
    def get_objective_architect_prompt(information_list: str = "", feedback: str = ""):
        prompt = PromptTemplate.from_template(
            """<system>
        <role>Objective Architect</role>
        <purpose>Transform course information into structured objectives aligned to Bloom's taxonomy.</purpose>
        
        <instructions>
        1. **Topic & Summary**: Extract topic and write 1-2 sentence summary
        2. **Tags**: 3-6 keywords capturing core concepts [mark inferred]
        3. **Prerequisites**: Essential knowledge/skills only [mark inferred]
        4. **Learning Outcomes**: 1-5 measurable outcomes using Bloom's language
        5. **Difficulty Level**: beginner | intermediate | advanced
        6. **Objectives** (1-5 max):
           - name, description, bloom_tag (1-6), smart (bool), status: "not_completed"
           - Scaffold progressively by complexity
        7. **Constraints** (type | description | value):
           - Types: time, resources, scope, audience, technology, assumption
        
        <rules>
        - Mark all inferred data with [inferred]
        - Merge duplicate entries
        - Validate objectives align to outcomes and constraints
        - Ensure difficulty matches prerequisites and Bloom's progression
        </rules>
        
        <feedback>
            {feedback}
        </feedback>
        
        Input Information:
        {information_list}
        </system>"""
        )
        return prompt.invoke(
            {"information_list": information_list, "feedback": feedback}
        ).to_string()

    @staticmethod
    def get_evaluator_oa_prompt(analyzed_data: AnalyzedData, messages: str = "") -> str:
        prompt = PromptTemplate.from_template(
            """Review the following analyzed data and assess its quality:

    **Topic:** {topic}
    **Summary:** {summary}
    **Tags:** {tags}
    **Prerequisites:** {prerequisites}
    **Learning Outcomes:** {learning_outcomes}
    **Difficulty:** {difficulty}
    **Objectives:**
    {objectives}
    **Constraints:**
    {constraints}

    Evaluate this data for:
    1. Completeness - Are all required fields populated?
    2. Consistency - Do objectives align with learning outcomes?
    3. Quality - Is the content accurate and well-structured?
    4. Relevance - Are tags and prerequisites appropriate?

    Compare it with the conversation to see if everything appropriate is contained:
    {messages}

    Provide specific feedback and indicate if this data meets quality standards."""
        )

        # Handle null analyzed_data
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
