import argparse
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions.get_files_info import get_files_info, schema_get_files_info


load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")


def parse_args():
    parser = argparse.ArgumentParser(
        prog="bootloader_ai_agent",
        description="Take a prompt arg from the command line and send to Gemini LLM",
    )
    parser.add_argument("user_prompt")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    client = genai.Client(api_key=API_KEY)
    model = "gemini-2.0-flash-001"

    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    """

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
        ]
    )

    messages = [
        types.Content(role="user", parts=[types.Part(text=args.user_prompt)])
    ]

    response = client.models.generate_content(
        model=model,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
        contents=messages,
    )

    print(f"Response text:\n{response.text}")
    if response.function_calls:
        print(f"Response function calls:\n{response.function_calls}")

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
