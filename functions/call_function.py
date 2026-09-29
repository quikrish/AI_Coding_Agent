import json
from functions.get_files_info import *
from functions.get_file_content import *
from functions.write_to_file import *
from functions.run_python_file import *
from collections.abc import Callable

available_functions = [
    schema_get_files_info,schema_get_file_content,schema_run_python_file,schema_write_file
]

def call_function(tool_call, verbose: bool = False) -> dict:

    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments or "{}")

    if verbose:
        print(f" - Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")

    function_map: dict[str, Callable[..., str]] = {
        "get_file_content": get_file_content,
        "get_files_info": get_files_info,
        "write_file": write_file,
        "run_python_file": run_python_file
        }

    if function_name in function_map:
        function_args["working_directory"] = "./calculator"
        result = function_map[function_name](**function_args)

        return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result,
        }


    else:
        return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": f"Error: Unknown function: {function_name}",
        }