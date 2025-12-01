# AI Agent for Code Development

This is a toy project to use Gemini Text-out models to build a code generation/manipulation agent. There will be more
work required to turn this into something like a CLI tool that can be used with any package. I may come back to this
project later, but because there exist more polished and more secure agentic AI tools that can be integrated into IDEs,
it didn't seem worthwhile to continue building on this project.

I am instead using the lessons learned from this project to build other agentic AI tools where the use of an
independent agent simplifies developer experience.

This project is my implementation of the [boot.dev](https://www.boot.dev/) Guided Project to
[Build an AI Agent in Python](https://www.boot.dev/courses/build-ai-agent-python).

## Contents

The Agentic AI loops and tool definitions are a part of the `main.py` script, which is also the CLI tool to give
high-level commands. The functions and `FunctionDeclaration` objects required to allow tool-based actions by the
Gemini model are defined in the `functions/` directory.

This project uses the `gemini-2.0-flash` model because this is the model with one of the highest RPM and RPD
rate limits, and is great for experimenting/making mistakes with. I have tested this with `gemini-2.5-flash`, but not
with the new Gemini 3.

The actual "package", where code is added/replaced/removed, is in the `calculator/` directory. This consists of a basic
calculator Python app. The AI agent has its access restricted to this folder, and can add features and associated
tests, and run them to verify correctness.

## How to run

```bash
python main.py "<prompt>"
```

For example:
```bash
python main.py "Add the ability to host a local webserver on 127.0.0.1 at port 8080 that uses the calculator app"
```

Logs are written into `action_log_{datetime_at_execution}.log` files, consisting of the planning, thinking, and
steps taken by the agent.
