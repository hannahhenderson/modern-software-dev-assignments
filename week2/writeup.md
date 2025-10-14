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
``` 



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
Prompt: 
```
TODO
``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```

### Exercise 3: Refactor Existing Code for Clarity
Prompt: 
```
TODO
``` 

Generated/Modified Code Snippets:
```
TODO: List all modified code files with the relevant line numbers. (We anticipate there may be multiple scattered changes here – just produce as comprehensive of a list as you can.)
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
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