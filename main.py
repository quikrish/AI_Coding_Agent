import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI
import argparse
from prompts import system_prompt
from functions.call_function import available_functions, call_function

load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")

if not api_key:
    raise RuntimeError("API key not found")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

#take command-line arguments from the user using argparse module 
parser = argparse.ArgumentParser() #This creates an ArgumentParser object

# this tells the parser that my program expects an agrgument called user_prompt
parser.add_argument("user_prompt", type=str, help="User prompt")

#Add a new optional command-line argument, --verbose. argparse makes this easy – "store_true" means the argument will be parsed as a boolean value of True if the flag is set, otherwise False
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
# This is where argparse actually looks at the command line.
args = parser.parse_args()

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": args.user_prompt},
]
# model-calling logic in a loop, so the agent can iterate on a task until it's done working and has a final response for the user.
for _ in range(20):
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        tools=available_functions,
    )

    if args.verbose and response.usage is not None:
        print(f"User prompt: {args.user_prompt}")
        print("Prompt tokens: ",response.usage.prompt_tokens)
        print("Response tokens: ", response.usage.completion_tokens)

    # capture assistance response
    message = response.choices[0].message

    # add the assistant message to the conversation
    messages.append(message)

    if message.tool_calls:
        for tool_call in message.tool_calls:
            result_message = call_function(tool_call, args.verbose)

            if not result_message["content"]:
                raise Exception("Tool call returned no content")

            # Add the tool result to the conversation
            messages.append(result_message)

            if args.verbose:
                print(f"-> {result_message['content']}")
    else:
        print(message.content)
        break
else:
    print("the agent failed to reach a final answer")
    sys.exit(1)

def main():
    # print("Hello from ai-agent!")
    pass


if __name__ == "__main__":
    main()
