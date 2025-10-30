import os

from google.genai import types

from .config import MAX_CHARS


def get_file_content(working_directory, file_path):
    try:
        working_directory_abs_path = os.path.abspath(working_directory)
        file_abs_path = os.path.normpath(os.path.join(working_directory_abs_path, file_path))

        if not file_abs_path.startswith(working_directory_abs_path):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(file_abs_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        file_size = os.path.getsize(file_abs_path)
        with open(file_abs_path, "r") as f:
            file_content_string = f.read(MAX_CHARS)

        if len(file_content_string) < file_size:
            file_content_string += f'\n[...File "{file_path}" truncated at {MAX_CHARS} characters]'

        return file_content_string

    except Exception as e:
        return f"Error: {e}"


schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Read file contents, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path for any file whose content must be read, relative to the working directory.",
            ),
        },
    ),
)
