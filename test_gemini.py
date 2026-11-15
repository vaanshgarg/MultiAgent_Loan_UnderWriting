
import asyncio
from dotenv import load_dotenv
from agent_framework import Agent
from config import create_gemini_client

load_dotenv()


async def main():
    print("Connecting to Gemini...")

    client = create_gemini_client()

    agent = Agent(
        client=client,
        name="GeminiTestAgent",
        instructions=(
            "You are a loan underwriting assistant. "
            "Answer briefly and clearly."
        ),
    )

    response = await agent.run(
        "Explain what EMI means in one sentence."
    )

    print("\nGemini response:")
    print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
