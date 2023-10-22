# PyTagScript

## Installation

```bash
pip install git+https://github.com/Therosin/PyTagScript
```

### Usage

```python
# import the module
from PyTagScript import TagScript, TagScriptSyntaxError, TagScriptRuntimeError, TagScriptArgumentError, TagScriptSandboxError

# Initialize TagScript
tag_scripts = TagScript(name="tag_scripts")
```

### Syntax 🔭

- `tagscript: expression`: The expression is the Tagscript expression you want to evaluate. It can be any valid Python expression.
- `tagscript: (param1, param2, namedParam=defaultValue) => expression`: You can also pass parameters to your Tagscript expression.
  - The parameters are passed as a comma-separated list within parentheses.

#### tagscript Scope 🔭

tagscript expressions are constrained to:

- Basic Python functionalities.
- External modules or objects explicitly registered via `tagscript_globals`.

You can extend the power of TagScripts by registering additional globals during TagScript initialization or later using the `register_tagscript_globals` method.

```python
# During Initialization
tag_scripts = TagScript(name="tag_scripts", env={"datetime": datetime})
# Extending functionalities
tag_scripts.register_tagscript_globals({"math": math})
```

#### Calling TagScript Functions 🗣️

- `tag_scripts.run("tagscript: 'Hello, World!'"))` >> Hello, World!
- `tag_scripts.run("tagscript: (param) => f'Hello, {param}!'", ["World"])` >> Hello, World!
- `tag_scripts.run("tagscript: (msg, name='World') => f'Hello, {name}. {msg}!'", ["Welcome, Everyone."], name="Universe")` >> Hello, Universe. Welcome, Everyone.!

## Quality Assurance: Test-Driven Approach 🛠️

Comprehensive test suites assure that PyTagScript operates reliably, covering everything from tags to intricate error-handling scenarios.

## License

[MIT](https://choosealicense.com/licenses/mit/) © 2023 [Therosin](https://github.com/Therosin)

[LICENSE](./LICENSE)
