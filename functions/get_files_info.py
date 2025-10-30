import os

from google.genai import types


def get_files_info(working_directory, directory="."):
    try:
        working_directory_abs_path = os.path.abspath(working_directory)
        directory_abs_path = os.path.normpath(os.path.join(working_directory_abs_path, directory))
        
        if not directory_abs_path.startswith(working_directory_abs_path):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        if not os.path.isdir(directory_abs_path):
            return f'Error: "{directory}" is not a directory'

        directory_contents = os.listdir(directory_abs_path)
        enrich_directory_contents = [
            {
                "file_name": file_name,
                "file_size": os.path.getsize(os.path.join(directory_abs_path, file_name)),
                "is_dir": os.path.isdir(os.path.join(directory_abs_path, file_name))
            }
            for file_name in directory_contents
        ]
        response = ""
        for entry in enrich_directory_contents:
            response += f"- {entry['file_name']}: file_size={entry['file_size']} bytes, is_dir={entry['is_dir']}\n"
        return response

    except Exception as e:
        return f"Error: {e}"


schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)
