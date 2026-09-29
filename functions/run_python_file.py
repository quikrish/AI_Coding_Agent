import os
import subprocess

def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
        try:
            working_dir_abs = os.path.abspath(working_directory)
        
            target_file = os.path.normpath(os.path.join(working_dir_abs,file_path))
    
            valid_target_file = (
                os.path.commonpath([working_dir_abs, target_file])
                == working_dir_abs
                )
                
            if not valid_target_file:
                return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
              
            if not os.path.isfile(target_file):
                return f'Error: "{file_path}" does not exist or is not a regular file'

            if not target_file.endswith('.py'):
                  return f'Error: "{file_path}" is not a Python file'
    
            command = ["python", target_file]
            if args:
                command.extend(args)
            command_output = subprocess.run(
                 command, 
                 cwd = working_dir_abs, 
                 capture_output=True, 
                 timeout=30, 
                 text=True
                 )
            output = []
            if command_output.returncode:
                 output.append(f'Process exited with code {command_output.returncode}')
            if command_output.stdout:
                output.append(f'STDOUT:{command_output.stdout}')
            if command_output.stderr:
                output.append(f'STDERR:{command_output.stderr}')
            if not command_output.stdout and not command_output.stderr:
                output.append(f'No output produced')

            return '\n'.join(output)
        except Exception as e:
            return f"Error: {e}"


schema_run_python_file = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": "Runs a Python file within the permitted working directory and optionally passes command-line arguments to it.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the Python file to run, relative to the working directory.",
                },
                "args": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Optional list of command-line arguments to pass to the Python file.",
                },
            },
            "required": ["file_path"],
        },
    },
}