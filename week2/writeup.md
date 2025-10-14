# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: Hannah Henderson \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature

Analyze the existing `extract_action_items()` function in `week2/app/services/extract.py`, which currently extracts action items using predefined heuristics.

Your task is to implement an **LLM-powered** alternative, `extract_action_items_llm()`, that utilizes Ollama to perform action item extraction via a large language model.

Some  tips:
- To produce structured outputs (i.e. JSON array of strings), refer to this documentation: https://ollama.com/blog/structured-outputs 
- To browse available Ollama models, refer to this documentation: https://ollama.com/library. Note that larger models will be more resource-intensive, so start small. To pull and run a model: `ollama run {MODEL_NAME}`


Prompt: 
```
walk me through what's happening in extract.py.

what prefixes count as a "note" prefix?

give me a pseudocode list of the functionality that extract_action_items performs

tell me how you would approach prompting an LLM to perform those key behaviors

starting with the smallest ollama model possible, what model would you import and how would you prompt it to achieve this outcome?

what calls extract_action_items today?

how should i update the code to point to extract_with_ollama

hmmm. i generally like these recommendations, but i'd like to be able to toggle between functions in the code and in tests. i'd like to see the results if i use extract_with_ollama, extract_action_items OR simple_extract_with_ollama.

For the code present, we get this error:
```
Import "ollama" could not be resolved
```
How can I resolve this? If you propose a fix, please make it concise.

before i run that, what are the pros and cons of externally-managed vs. virtual? I'm used to running things from iterm

<selected the virtual environment and tested some install commands>

python test_extraction_methods.py

<yes, install missing dependencies>
<run the tests, cursive tells me what things are/aren't working>

you said the LLM methods work but need prompt engineering for clean output. tell me what is going wrong and what fixes you recommend. explain your reasoning

keep all of those changes
<run the tests>

explain your reasoning, how might you imprvoe the phi3:mini implemetnation even further?

I only have the option to revert blocks when I go to view your changes. I want to accept all of your recommended changes

hmmm this looks mostly correct, but the 'content' for the 'system' 'role' is no longer referencing the big `prompt` text. 

run tests again

are there still changes that i need to review?

now, i want the default extraction tool to use the LLM-powered function. let's go with the smallest possible LLM function
``` 

#### Instructions

Setting up virtual environment:
```
python3 -m venv venv
source venv/bin/activate && pip install ollama

<!-- test that it works -->
source venv/bin/activate && python -c "from ollama import Client; print('✅ Ollama import successful!')"
```

Going forward, to work in this project run: `source venv/bin/activate`
Then you can run your code normally:
```
# Test the extraction methods
python test_extraction_methods.py

# Run the API server
python -m uvicorn app.main:app --reload

# Run tests
pytest tests/test_extract.py -v
```

This should be auto-activated because you ran the line:
```
echo 'cd /Users/hannahhenderson/Desktop/stanford2025/modern-software-dev-assignments/week2 && source venv/bin/activate' >> ~/.zshrc
```

Key behaviors:
Primary detection: Looks for bullet points, keyword prefixes (todo:, action:, next:), and checkbox markers ([ ], [todo])
Cleaning: Removes bullet prefixes and checkbox markers from matched lines
Fallback: If no obvious action items found, splits text into sentences and looks for imperative verbs
Deduplication: Removes duplicates case-insensitively while preserving original order
Imperative detection: Uses a fixed set of action verbs to identify command-like sentences

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```

### Exercise 2: Add Unit Tests
Write unit tests for `extract_action_items_llm()` covering multiple inputs (e.g., bullet lists, keyword-prefixed lines, empty input) in `week2/tests/test_extract.py`.

Prompt: 
```
tell me about the sample inputs for `extract_action_items_llm()`

what kind of unit tests leverage those examples?

add those test cases. also add some "not in" assertions

<skipped a few here. tl;dr, the models fail the more extensive tests>

i want to test the differences between the hueristic approach and the LLM approach, so i do not want to combine them, they should remeain sepate. suggest changes only to the LLM prompts and framing.
use chain-of-thought for the small models and the model-specific optimizations


``` 

### Exercise 3: Refactor Existing Code for Clarity
Prompt: 
```
alright. look at the code currently. pay special attention to the extract* files. what could be construed as confusing? how could the code be made more clear for a human reader/coder/editor?

yes, implement these improvements

do modern python developers tend to use classes? i thought they didn't

what other files have changed? look at them, what could be improved?

yes, refactor

ignore writeup.md and assignment.md. what refactoring makes sense?

_here, i asked chatgpt for help understanding the gold standard of python and asked for help assembling the following prompt:

You are a senior Python engineer. Improve the selected code and surrounding module(s) to a modern “gold standard” while keeping external behavior the same unless I explicitly permit changes.

Goals (ranked):
1) Correctness & safety
2) Clarity & maintainability
3) Performance (only when it stays readable)
4) Consistent style with modern tools

Apply these practices:
- Python 3.12 idioms: pattern matching where appropriate, f-strings, `pathlib`, `enumerate`/`zip`, context managers, `dataclasses` (or Pydantic models if I’m already using them), `functools`/`itertools` when clearer.
- Types: add precise type hints; prefer `TypedDict`, `Protocol`, and `Literal` over `Any`. No unused/lying types. Public functions must be fully typed.
- Errors: no bare `except`; catch specific exceptions; use `raise … from e`; add helpful messages. Validate inputs at module boundaries.
- Mutability: avoid mutable defaults; prefer immutability in dataclasses where feasible; copy user-supplied collections before mutating.
- API/structure: extract long functions; name things descriptively; limit function/class responsibilities; remove dead code; reduce parameter/boolean soup.
- IO & networking: timeouts, retries/backoff are explicit; deterministic randomness via seeds; no hidden global state.
- Logging/observability: use stdlib `logging` with structured, leveled events (no prints in library code).
- Security: never eval/exec on user data; sanitize/validate external inputs (env, HTTP, files).
- Performance: eliminate obvious N^2 hotspots; avoid repeated work; use lazy iteration where safe; document any trade-offs.

Style & tooling assumptions (do not change unless I say so):
- Formatter: Black (line length 88) and isort OR Ruff-as-one-tool (preferred).
- Linting: Ruff rules roughly covering pyflakes/pep8/isort, plus common flake8 rules (no unused imports/vars, no shadowing, no wildcard imports).
- Types: mypy (or pyright) clean on strict-ish settings (no implicit Optionals, disallow untyped defs where practical).
- Tests: pytest. Preserve behavior; add/adjust tests when refactors make behavior clearer.

What to deliver:
1) A concise plan: bullet points of the key issues you see and the refactors you’ll do.
2) A minimal, review-friendly diff of changes (group related edits; avoid churn).
3) Notes: any behavior-affecting changes, new dependencies, or TODOs for follow-ups.
4) Quality gates to run locally (commands), including ruff/black/mypy/pytest invocations.

Refactor heuristics:
- Prefer small, composable functions and pure helpers.
- Push side effects to edges; keep core logic pure/testable.
- Replace ad-hoc dicts/tuples of mixed data with typed dataclasses or Protocols when it clarifies intent.
- Prefer `pathlib.Path` over `os.path`; `subprocess.run(..., check=True)` over `os.system`.
- Replace manual string formatting with f-strings; replace manual resource cleanup with context managers.
- Keep public API stable; mark any deprecations clearly with docstrings and comments.
- Inline trivial indirections; de-duplicate code via well-named helpers.
- Add Google- or NumPy-style docstrings to public functions/classes.

If something is ambiguous, ask me concise yes/no questions; otherwise proceed with safe, incremental improvements.

At the end, show:
- The diff
- A short “before vs after” complexity/readability summary
- The exact commands to verify: 
  - If using Ruff: `ruff check . && ruff format .`
  - Else: `black . && isort . && flake8`
  - Types: `mypy .` (or `pyright`)
  - Tests: `pytest -q`




``` 

Generated/Modified Code Snippets:
```
TODO: List all modified code files with the relevant line numbers. (We anticipate there may be multiple scattered changes here – just produce as comprehensive of a list as you can.)
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
1. Integrate the LLM-powered extraction as a new endpoint. Update the frontend to include an "Extract LLM" button that, when clicked, triggers the extraction process via the new endpoint.

2. Expose one final endpoint to retrieve all notes. Update the frontend to include a "List Notes" button that, when clicked, fetches and displays them.


Prompt: 
```
TODO
``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```


### Exercise 5: Generate a README from the Codebase
Prompt: 
```
TODO
``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 