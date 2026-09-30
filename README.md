AI Agent

A command-line AI coding agent built in Python as part of a hands-on backend/AI agent project.

The project uses the OpenAI Python SDK with OpenRouter to communicate with an LLM. The agent is gradually being extended with tools that allow it to inspect files, read files, write files, and execute Python programs inside a restricted working directory.

Features

Send prompts to an LLM from the terminal with argparse.

Use a system prompt to define the agent's role and behavior.

Expose Python functions to the LLM through OpenAI-compatible tool schemas.

List files and directories with metadata.

Read file contents with a character limit and truncation handling.

Create and overwrite files within the permitted working directory.

Execute Python files with controlled working-directory access.

Iterate through tool calls until the model produces a final response.

Limit agent iterations to prevent an endless tool-calling loop.

Restrict file operations to a configured working directory for safety.

Project Structure

AI_Agent/
├── calculator/
│   ├── main.py
│   ├── tests.py
│   └── pkg/
│       ├── calculator.py
│       └── render.py
├── functions/
│   ├── call_function.py
│   ├── get_files_info.py
│   ├── get_file_content.py
│   ├── run_python_file.py
│   └── write_to_file.py
├── prompts.py
├── main.py
├── test_get_files_info.py
├── test_write_file.py
└── README.md

Requirements

Python 3.10+

uv

An OpenRouter API key

Setup

Create an environment file named .env in the project root:

OPENROUTER_API_KEY=your_api_key_here

The application loads the variable with python-dotenv and retrieves it through os.environ.

Install dependencies with your project's uv configuration, then run the application from the project root.

Running the Agent

The agent accepts a required positional prompt and an optional --verbose flag.

uv run main.py "what files are in the root?"

For additional debugging information:

uv run main.py --verbose "how does the calculator render results to the console?"

--verbose prints information such as the prompt, token usage, tool calls, and tool results.

How It Works

At a high level, the agent follows this loop:

User prompt
    ↓
System prompt + conversation history
    ↓
LLM
    ↓
Tool call or final response
    ↓
If tool call → execute Python function
    ↓
Append assistant message + tool result to history
    ↓
Call LLM again
    ↓
Repeat until final response or iteration limit

The main components are:

System Prompt

prompts.py contains instructions that define the agent's role, behavior, and tool-usage rules.

Tool Schemas

Each tool defines a JSON-compatible schema describing its name, purpose, and accepted parameters. These schemas are passed to the model through the tools parameter of client.chat.completions.create().

Tool Dispatcher

functions/call_function.py maps tool names returned by the model to real Python functions.

Conceptually:

function_map = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
}

The dispatcher parses the JSON arguments returned by the model, injects the controlled working directory, calls the selected function, and wraps the result as a tool message.

Conversation History

The agent stores messages using the chat message format:

[
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt},
    # assistant tool-call message
    # tool result message
]

Keeping these messages allows the model to see what it previously requested and what each tool returned.

Available Tools

get_files_info

Lists the contents of a directory relative to the configured working directory and returns each item's name, size, and directory status.

Example:

- calculator.py: file_size=1721 bytes, is_dir=False
- render.py: file_size=376 bytes, is_dir=False

get_file_content

Reads a file inside the permitted working directory. The function limits the amount of content read and reports when a file has been truncated.

write_file

Creates or overwrites a file inside the permitted working directory. Missing parent directories are created automatically.

run_python_file

Runs a Python file from within the permitted working directory and returns the program's output or an error message.

Path Safety

The file-related tools do not trust paths supplied by the LLM. They build a target path from a controlled working_directory, normalize it, and verify that the target remains inside the permitted directory.

The basic pattern is:

working_dir_abs = os.path.abspath(working_directory)

target_path = os.path.normpath(
    os.path.join(working_dir_abs, requested_path)
)

valid_target_path = (
    os.path.commonpath([working_dir_abs, target_path])
    == working_dir_abs
)

This prevents requests such as ../ or /tmp/... from escaping the agent's allowed workspace.

The working_directory is intentionally injected by the application rather than being controlled by the LLM.

Tool Calling Model

The LLM does not directly execute Python functions. It receives tool schemas and can return a request such as:

function name: get_files_info
arguments: {"directory": "pkg"}

The Python application then:

Parses the JSON arguments.

Looks up the function by name.

Injects the application-controlled working directory.

Executes the Python function.

Packages the result as a tool message.

Adds the result to the conversation history.

Sends the updated history back to the model on the next iteration.

Development Notes

This project is intentionally built incrementally to demonstrate the core components of an AI agent:

LLM
 +
System prompt
 +
Tool schemas
 +
Tool execution
 +
Conversation state
 +
Feedback loop
 =
AI agent

The agent loop is capped at a fixed number of iterations to prevent runaway tool calls.

Testing

Run the file-operation test modules from the project root:

uv run test_get_files_info.py
uv run test_write_file.py

You can also exercise the agent directly with prompts such as:

uv run main.py "what files are in the pkg directory?"
uv run main.py "read main.py"
uv run main.py "create a new text file called example.txt"
uv run main.py "run the calculator tests"

Security Considerations

Giving an LLM access to filesystem and code-execution tools is powerful. The project therefore uses application-level guardrails in addition to system-prompt instructions.

The system prompt guides the model, while the Python tools enforce the actual filesystem restrictions. Tool functions return errors as strings so the model can observe failures and adjust its next action.
