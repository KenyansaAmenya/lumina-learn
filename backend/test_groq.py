import asyncio
from ai_service import Groqservice
import os
from dotenv import load_dotenv

load_dotenv()

async def test_groq():
    service = Groqservice()
    result = await service.generate_question("World History", "medium")
    print(result)

asyncio.run(test_groq())