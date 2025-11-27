import argparse
import os
import logging

from datetime import datetime
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

LOGGER = logging.getLogger(__name__)
FILE_HANDLER = logging.FileHandler(
    f"action_log_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.log",
    mode="w",
    encoding="utf-8",
)
FILE_HANDLER.setFormatter(
    logging.Formatter(
        "{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d:%H:%M:%S",
    )
)
LOGGER.addHandler(FILE_HANDLER)
LOGGER.setLevel(logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="bootloader_ai_agent",
        description="Take a prompt arg from the command line and send to Gemini LLM",
    )
    parser.add_argument("user_prompt")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def call_function(function_call_part, verbose=False) -> types.Part:
    LOGGER.info(f" - Calling function: {function_call_part.name}({function_call_part.args})")
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
        return types.Part.from_function_response(
            name=function_call_part.name, response={"error": f"Unknown function: {function_call_part.name}"}
        )

    try:
        response = function_map[function_call_part.name]("./calculator", **function_call_part.args)
    except Exception as e:
        return types.Part.from_function_response(name=function_call_part.name, response={"error": str(e)})
    return types.Part.from_function_response(name=function_call_part.name, response={"result": response})


@retry(reraise=True, stop=stop_after_attempt(2), retry=retry_if_exception_type(errors.ClientError))
def generate_content_helper(system_prompt, messages):
    return client.models.generate_content(
        model=model,
        config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt),
        contents=messages,
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

    All paths you provide should be relative to the working directory. You do not need to specify the working directory
    in your function calls as it is automatically injected for security reasons.

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
        print(f"Iteration {i}")
        response = generate_content_helper(system_prompt, messages)

        if not response.function_calls or not response.candidates:
            LOGGER.info(f"Final Response: {response.text}")
            print(f"Final Response: {response.text}")
            break

        for candidate in response.candidates:
            if not candidate.content:
                continue
            messages.append(candidate.content)
            if not candidate.content.parts:
                continue

            candidate_response_content = types.Content(role="tool", parts=[])
            assert candidate_response_content.parts is not None
            for part in candidate.content.parts:
                if part.text:
                    LOGGER.info(part.text.strip("\n"))
                    if args.verbose:
                        print(part.text)

                if part.function_call:
                    function_call_result = call_function(part.function_call, verbose=args.verbose)
                    if not (
                        hasattr(function_call_result, "function_response")
                        and function_call_result.function_response is not None
                        and hasattr(function_call_result.function_response, "response")
                        and function_call_result.function_response.response is not None
                    ):
                        raise RuntimeError(
                            f"Response content from call_function {part.function_call.name} does not "
                            "have appropriate format"
                        )
                    if args.verbose:
                        print(f"-> {function_call_result.function_response.response}")
                    candidate_response_content.parts.append(function_call_result)
            messages.append(candidate_response_content)
        sleep(4)
    else:
        raise RecursionError("Failed to get expected response before max iterations.")

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        if response.usage_metadata:
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
