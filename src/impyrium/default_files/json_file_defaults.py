from .default_file import DefaultFile
from . import defaults

inputsFile = DefaultFile(f"{defaults.JSON_FOLDER}/{defaults.INPUTS_FILE}",
"""\
[
    {
        "left_trigger": "<ctrl>+[",
        "right_trigger": "<ctrl>+]",
        "type": "encoder",
        "reg_link": "python_encoders::encoder0.py"
    },
    {
        "trigger": "<ctrl>+1",
        "reg_link": "python_commands::test0.py"
    },
    {
        "trigger": "2",
        "reg_link": "python_commands::test1.py"
    }
]
"""
)

registry = DefaultFile(f"{defaults.JSON_FOLDER}/{defaults.REGISTRY_FILE}",
"""
[]
"""
)

folderCommands = DefaultFile(f"{defaults.JSON_FOLDER}/{defaults.FOLDER_COMMANDS_FILE}",
f"""
[
    {{
        "name": "python",
        "path": "{defaults.FOLDER_COMMANDS_TEST_COMMANDS_PATH}",
        "id": "python_commands",
        "input_type": "button"
    }},
    {{
        "name": "python",
        "path": "{defaults.FOLDER_COMMANDS_TEST_ENCODERS_PATH}",
        "id": "python_encoders",
        "input_type": "encoder"
    }}
]
"""
)


