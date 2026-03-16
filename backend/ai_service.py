# Phase 2: Groq Integration
# This will contain:
# - Groq client initialization
# - Prompt builders for correct/incorrect answers
# - Question generation functions

import os
from groq import AsyncGroq
from typing import Dict, Any 
import json
from config import get_settings

class Groqservice:
    def __init__(self):
        settings = get_settings()
        self.client = AsyncGroq(api_key=settings.groq_api_key)
        self.model = "llama-3.1-8b-instant"

    def build_feedback_prompt(
        self,
        topic: str,
        question: str,
        student_answer: str,
        correct_answer: str,
        is_correct: bool
    ) -> str:
        """Build context-rich prompt for personalized feedback."""

        if is_correct:
            return f"""You are an encouraging tutor. The student got this {topic} question RIGHT.
            Question: {question}
            Student's Answer: {student_answer}
            
            Provide feedback that:
            1. Congratulates them specifically on what they understood
            2. Explains WHY their answer is correct (renforce the concept)
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

    def _build_question_generation_prompt(
        self,
        topic: str,
        difficulty: str,
        question_type: str = "multiple choice"
    ) -> str:
        """Build prompt for generating quiz questions."""  

        return f"""Generate a {difficulty} level {question_type} question about {topic}.
        
        
        Respond ONLY in this JSON format (no markdown, no extra text):
        {{
            "question": "The question text here",
            "options": ["A) option1", "B) option2", "C) optionn3", "D) option4"],
            "correct_answer": "A) option1",
            "explaination": "Brief explanation of why this is correct",
            "hint": "A subtle hint without giving away the answer"
        }}
        
        Requirements: 
        - Question should test understanding, not just memorization
        - Difficulty: {difficulty} (easy/medium/hard)
        - All 4 options should be plausible
        - Explanation should teach the underlying concept"""

    async def generate_feedback(
        self,
        topic: str,
        question: str,
        student_answer: str,
        correct_answer: str,
        is_correct: bool
    ) -> str:
        """Generate personalized feedback using Groq."""

        prompt = self.build_feedback_prompt(
            topic, question, student_answer, correct_answer, is_correct
        )             

        try: 
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=300,
                timeout=10.0
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            # fallback if groq fails
            print(f"Groq error: {e}")
            if is_correct:
                return f" Correct! Great job understanding {topic}."
            else:
                return f" Not quite. The correct answer was: {correct_answer}.\nKeep practicing {topic}!"  

    async def generate_question(
        self, 
        topic: str,
        difficulty: str = "medium"
    ) -> Dict[str, Any]:
        """Generate a new quiz question using Groq."""

        prompt = self._build_question_generation_prompt(topic, difficulty)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a curriculum expert. Generate valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=500,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            return json.loads(content)

        except Exception as e:
            print(f"Question generation error: {e}")
            # Fallback question
            return {
                "question": f"Sample {topic} question ({difficulty})",
                "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                "correct_answer": "A) Option 1",
                "explaination": "This is a fallback question due to generation error.",
                "hint": "Review the basics of this topic."
            }    

    async def generate_hint(
        self,
        topic: str,
        question: str,
        student_previous_attempts: int = 0
    ) -> str:
        """Generate a contextual hint without giving away the answer."""

        hint_intensity = "subtle" if student_previous_attempts < 2 else "stronger"
        
        prompt = f"""The student is stuck on this {topic} question: {question}
        
        Provide a {hint_intensity} hint that:
        - Guides their thinking process
        - Does NOT give away the answer
        - References the concept being tested
        - Is under 100 words"""
        
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

groq_service = Groqservice()                        

