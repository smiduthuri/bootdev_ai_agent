import os

from google.genai import types


def write_file(working_directory, file_path, content):
    try:
        working_directory_abs_path = os.path.abspath(working_directory)
        file_abs_path = os.path.normpath(os.path.join(working_directory_abs_path, file_path))
        if not file_abs_path.startswith(working_directory_abs_path):
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        if not os.path.exists(file_abs_path):
            file_dir_abs_path = os.path.dirname(file_abs_path)
            if not os.path.isdir(file_dir_abs_path):
                os.makedirs(file_dir_abs_path)
        elif os.path.isfile(file_abs_path):
            os.remove(file_abs_path)

        with open(file_abs_path, "w") as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except Exception as e:
        return f"Error: {e}"


schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Write or overwrite file contents, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path for the file to be written to, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to be written to the file."
            )
        },
    ),
)
