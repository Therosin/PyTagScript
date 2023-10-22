import logging
import re

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

# Version of the TagTemplatesYaml package
template_manager_version = "1.0"

"""
    TagScript is a simple scripting language that allows for dynamic tags in templates.
    for all intents and purposes, its a wrapper around lambda functions with a modified syntax to support serializing and deserializing.
    security is handled via simple sandboxing, with a mutable environment.

    TagScript syntax:
        - basic syntax with no arguments:
            `tagscript: code`
            eg: `tagscript: 1 + 1` #- returns: 2
        - syntax with arguments:
            `tagscript: (args...) => code`
            eg: `tagscript: (a, b) => a + b` #- called with `(1, 1)` returns: 2
"""

safe_builtins = dict(__builtins__)
del safe_builtins["eval"]
del safe_builtins["exec"]
del safe_builtins["open"]
# remove all the unsafe builtins

unsafe_modules = [
    "os",
    "sys",
    "subprocess",
    "shutil",
    "importlib",
    "importlib.*",
]


def safe_import(name, *args, **kwargs):
    if name in unsafe_modules:
        raise ImportError(f"Importing {name} is not allowed")
    return __import__(name, *args, **kwargs)


safe_builtins["__import__"] = safe_import


class InvalidTagScriptError(Exception):
    """
    Base class for all TagScript errors.
    """

    pass


class TagScriptSyntaxError(InvalidTagScriptError):
    """
    Raised when a syntax error is encountered in a TagScript.
    """

    pass


class TagScriptRuntimeError(InvalidTagScriptError):
    """
    Raised when a runtime error is encountered in a TagScript.
    """

    pass


class TagScriptArgumentError(InvalidTagScriptError):
    """
    Raised when a TagScript is called with invalid arguments.
    """

    pass


class TagScriptSandboxError(InvalidTagScriptError):
    """
    Raised when a sandbox error is encountered in a TagScript.
    """

    pass


# regex to detect tagscript syntax
# this will match tagscript: code and tagscript: (args...) => code
tagscript_param_regex = re.compile(r"tagscript: \((.*)\)\s*=>\s*(.*)|tagscript: (.*)")


def parseTagScript(code):
    """
    Parse a TagScript.
    Returns a tuple of (is_tagscript, code, args)
    is_tagscript: bool - whether or not the code is a tagscript
    code: str - the code to run
    args: list - the arguments to pass to the code
    """
    found = re.match(tagscript_param_regex, code)
    if found:
        groups = found.groups()
        if groups[2] is not None:
            # tagscript: code
            parsed_code = groups[2]
            logger.debug(f"TagScript parsed without Args: {code} -> {parsed_code}")
            return True, parsed_code, []
        elif groups[0] is not None and groups[1] is not None:
            # tagscript: (args...) => code
            parsed_args, parsed_code = groups[0], groups[1]
            logger.debug(
                f"TagScript parsed with Args: {code} -> ({parsed_args}) {parsed_code}"
            )
            return True, parsed_code, [arg.strip() for arg in parsed_args.split(",")]

        # if we get here, it's not a tagscript
        return False, None, None


# TagScript class
class TagScript:
    def __init__(self, name="default", env={}):
        """
        Create a new TagScript object.
        env: dict - the environment to use for the TagScript
        """
        self.name = name
        tagscript_env = {
            "__builtins__": safe_builtins.copy(),
            "logger": logging.getLogger(f"TagScript.{name}"),
        }
        tagscript_env.update(env)
        self.env = tagscript_env

    def run(self, code, args=[], **kwargs):
        # try to parse the code
        is_tagscript, parsed_code, parsed_args = parseTagScript(code)
        logger.debug(f"TagScript.{self.name}: {code} -> ({parsed_args}) {parsed_code}")
        if not is_tagscript:
            raise InvalidTagScriptError(
                f"Invalid TagScript: {code} in TagScript.{self.name}"
            )
        else:
            try:
                if parsed_args:
                    logger.debug(
                        f"TagScript.{self.name}: {parsed_args} -> ({args}) {parsed_code}"
                    )
                    # Create a lambda function with the given code and args
                    lambda_func = eval(
                        f"lambda {', '.join(parsed_args)}: {parsed_code}", self.env
                    )
                    return lambda_func(*args, **kwargs)
                else:
                    logger.debug(f"TagScript.{self.name}: {parsed_code}")
                    # No arguments, just evaluate the code
                    return eval(parsed_code, self.env)
            except Exception as e:
                raise TagScriptRuntimeError(
                    f"Error running TagScript: {code} in TagScript.{self.name}"
                ) from e

    def register_globals(self, globals):
        """
        Register multiple global variables in the TagScript environment.
        globals: dict - the globals to register
        """
        self.env.update(globals)

    def unregister_globals(self, globals):
        """
        Unregister multiple global variables in the TagScript environment.
        globals: dict - the globals to unregister
        """
        for key in globals:
            if key in self.env:
                del self.env[key]

    def __repr__(self):
        return f"""
        <TagScript {self.name}> {{
            "env": {self.env}
        }}
    """

    def __copy__(self):
        return TagScript(self.name, self.env)

    def __eq__(self, other):
        return self.name == other.name and self.env == other.env

    def __hash__(self):
        return hash(self.name) + hash(id(self.env))

    def __str__(self):
        return f"<TagScript {self.name}>"

    def __call__(self, code, *args, **kwargs):
        return self.run(code, *args, **kwargs)
