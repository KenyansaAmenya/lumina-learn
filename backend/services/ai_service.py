import json
from typing import Dict, Any, List

class AIService:
    def __init__(self, groq_client, model: str = "llama-3.1-8b-instant"):
        self.client = groq_client
        self.model = model
    
    async def generate_feedback(
        self,
        topic: str,
        question: str,
        student_answer: str,
        correct_answer: str,
        is_correct: bool
    ) -> str:
        prompt = self._build_feedback_prompt(
            topic, question, student_answer, correct_answer, is_correct
        )
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300,
                timeout=10.0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI error: {e}")
            return self._fallback_feedback(is_correct, topic, correct_answer)

    def _build_feedback_prompt(self, topic, question, student_answer, correct_answer, is_correct):
        if is_correct:
            return f"""You are an encouraging tutor. The student got this {topic} question RIGHT.
            Question: {question}
            Student's Answer: {student_answer}
            
            Provide feedback that:
            1. Congratulates them specifically on what they understood
            2. Explains WHY their answer is correct (reinforce the concept)
            3. Offers a brief "stretch challenge" or deeper insight
            4. Keep it warm, personal, and under 150 words
            
            Format: Friendly paragraph, no bullet points."""
        else:
            return f"""You are a supportive tutor. The student got this {topic} question WRONG.
            Question: {question}
            Correct Answer: {correct_answer}
            Student's Answer: {student_answer}
            
            Provide feedback that:
            1. Acknowledges their effort positively (never say "wrong")
            2. Explains the concept clearly using the question context
            3. Shows a simple example or analogy 
            4. Points out exactly where their answer went off track
            5. Suggests what to review
            6. Keep it encouraging and under 200 words
            
            Format: Friendly, educational tone. No bullet points."""

    def _fallback_feedback(self, is_correct, topic, correct_answer):
        if is_correct:
            return f"Correct! Great job understanding {topic}."
        return f"Not quite. The correct answer was: {correct_answer}.\nKeep practicing {topic}!"

    async def generate_question(self, topic: str, difficulty: str = "medium") -> Dict[str, Any]:
        prompt = self._build_question_prompt(topic, difficulty)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a curriculum expert. Generate valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Question generation error: {e}")
            return self._fallback_question(topic, difficulty)

    def _build_question_prompt(self, topic, difficulty):
        return f"""Generate a {difficulty} level multiple choice question about {topic}.
        
        Respond ONLY in this JSON format:
        {{
            "question": "The question text here",
            "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
            "correct_answer": "A) option1",
            "explaination": "Brief explanation of why this is correct",
            "hint": "A subtle hint without giving away the answer"
        }}
        
        Requirements: 
        - Question should test understanding, not just memorization
        - Difficulty: {difficulty}
        - All 4 options should be plausible"""

    def _fallback_question(self, topic, difficulty):
        return {
            "question": f"Sample {topic} question ({difficulty})",
            "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
            "correct_answer": "A) Option 1",
            "explaination": "Fallback question due to generation error.",
            "hint": f"Review the basics of {topic}."
        }

    async def generate_hint(self, topic: str, question: str, previous_attempts: int = 0) -> str:
        intensity = "subtle" if previous_attempts < 2 else "stronger"
        prompt = f"""The student is stuck on this {topic} question: {question}
        Provide a {intensity} hint that guides thinking without giving the answer.
        Under 100 words."""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return f"Think about the key concepts in {topic}. What principles apply here?"

    async def generate_teaching_insights(self, weak_areas_data: List[dict]) -> str:
        """Generate AI teaching recommendations based on weak areas."""
        context_lines = ["Student performance data:"]
        for area in weak_areas_data:
            accuracy = (area['correct_count'] / area['total_attempts'] * 100) if area['total_attempts'] > 0 else 0
            context_lines.append(
                f"- {area['topic']}: {accuracy:.1f}% accuracy "
                f"({area['correct_count']}/{area['total_attempts']} correct)"
            )
        
        prompt = f"""As an expert educator, analyze this student's weak areas:

{'\n'.join(context_lines)}

Provide:
1. Root cause analysis
2. 3 concrete intervention strategies  
3. Recommended resources
4. Timeline for improvement check

Keep under 300 words, encouraging and professional."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"AI analysis failed: {str(e)}")
