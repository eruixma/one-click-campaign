"""Main entry point for the Pega When Rule Agent."""

import asyncio
import os
import sys
from pathlib import Path

# Load .env file before importing google modules
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from pega_agent.agent import pega_when_rule_agent


def create_user_message(text: str) -> types.Content:
    """Create a user message Content object."""
    return types.Content(
        role="user",
        parts=[types.Part(text=text)]
    )


async def run_interactive():
    """Run the agent in interactive mode."""
    session_service = InMemorySessionService()
    runner = Runner(
        agent=pega_when_rule_agent,
        app_name="pega-when-rule-agent",
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name="pega-when-rule-agent",
        user_id="user",
    )

    print("=" * 60)
    print("Pega When Rule Agent")
    print("=" * 60)
    print("Convert natural language into Pega When Rules.")
    print("Type 'exit' or 'quit' to end the session.")
    print("Type 'examples' to see example inputs.")
    print("=" * 60)
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        if user_input.lower() == "examples":
            print("\nExample inputs you can try:")
            print("  - Standard exclusion for campaign 12345")
            print("  - Exclude customers under 18 or over 65")
            print("  - Check if customer has bonds maturing in 2 days")
            print("  - Valid RPQ with risk level between 1 and 5")
            print("  - Customers with investment account holding bonds")
            print()
            continue

        # Run the agent
        user_message = create_user_message(user_input)
        async for event in runner.run_async(
            session_id=session.id,
            user_id="user",
            new_message=user_message,
        ):
            if hasattr(event, "content") and event.content:
                if hasattr(event.content, "parts"):
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            print(f"\nAgent: {part.text}")

        print()


async def run_single_query(query: str):
    """Run a single query and return the result."""
    session_service = InMemorySessionService()
    runner = Runner(
        agent=pega_when_rule_agent,
        app_name="pega-when-rule-agent",
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name="pega-when-rule-agent",
        user_id="user",
    )

    result_text = ""
    user_message = create_user_message(query)

    async for event in runner.run_async(
        session_id=session.id,
        user_id="user",
        new_message=user_message,
    ):
        if hasattr(event, "content") and event.content:
            if hasattr(event.content, "parts"):
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        result_text += part.text

    return result_text


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Single query mode
        query = " ".join(sys.argv[1:])
        result = asyncio.run(run_single_query(query))
        print(result)
    else:
        # Interactive mode
        asyncio.run(run_interactive())


if __name__ == "__main__":
    main()
