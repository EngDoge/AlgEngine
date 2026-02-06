import re
import json
# from json_repair import repair_json

JSON_PATTERN = re.compile(r'```json\s*(.*?)\s*```', re.DOTALL)


def str2obj(string, obj=dict):
    match = re.search(JSON_PATTERN, string)
    if match:
        json_string = match.group(1)
        json_string = json_string.replace("'", '"')
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            print(e)
        else:
            return obj(**data) if obj is not None else data
    return obj() if obj is not None else None
    