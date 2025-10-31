import argparse
import os
import sys

from time import sleep

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from functions.get_file_content import get_file_content, schema_get_file_content
from functions.get_files_info import get_files_info, schema_get_files_info
from functions.run_python_file import run_python_file, schema_run_python_file
from functions.write_file import write_file, schema_write_file


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


@retry(reraise=True, stop=stop_after_attempt(2), retry=retry_if_exception_type(errors.ClientError))
def call_function(function_call_part, verbose=False) -> types.Content:
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    function_map = {
        "get_file_content": get_file_content,
        "get_files_info": get_files_info,
        "run_python_file": run_python_file,
        "write_file": write_file,
    }

    if function_call_part.name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": f"Unknown function: {function_call_part.name}"}
                )
            ]
        )

    response = function_map[function_call_part.name]("./calculator", **function_call_part.args)
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_call_part.name,
                response={"result": response}
            )
        ]
    )


if __name__ == "__main__":
    args = parse_args()
    client = genai.Client(api_key=API_KEY)
    model = "gemini-2.0-flash-001"

    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.

    Any questions about a calculator application can be answered by examining the files to which you are given access.
    """

    available_functions = types.Tool(
        function_declarations=[
            schema_get_file_content,
            schema_get_files_info,
            schema_run_python_file,
            schema_write_file,
        ]
    )

    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
    for i in range(20):
        response = client.models.generate_content(
            model=model,
            config=types.GenerateContentConfig(
                tools=[available_functions], system_instruction=system_prompt
            ),
            contents=messages,
        )

        if not any(
            [
                part.function_call is not None
                for candidate in response.candidates
                for part in candidate.content.parts
            ]
        ):
            print(response.text)
            break

        candidate_function_calls_made = False

        for candidate in response.candidates:
            if not candidate.content:
                continue
            messages.append(candidate.content)
            if not candidate.content.parts:
                continue
            for part in candidate.content.parts:
                if args.verbose and part.text:
                    print(part.text)

                if part.function_call:
                    function_call_result = call_function(part.function_call, verbose=args.verbose)
                    if (
                        not function_call_result.parts
                        or not hasattr(function_call_result.parts[0].function_response, "response")
                    ):
                        raise RuntimeError(
                            f"Response content from call_function {part.function_call.name} does not have appropriate format"
                        )
                    if args.verbose and function_call_result.parts[0].function_response:
                        print(f"-> {function_call_result.parts[0].function_response.response}")
                    messages.append(function_call_result)
        sleep(1)
    else:
        raise RecursionError("Failed to get expected response before max iterations.")


    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
