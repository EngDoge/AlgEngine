import re
import json
# from json_repair import repair_json

JSON_PATTERN = re.compile(r'```json\s*(.*?)\s*```', re.DOTALL)


def str_to_schema(string, schema=None):
    match = re.search(JSON_PATTERN, string)
    if match:
        json_string = match.group(1)
        json_string = json_string.replace("'", '"')
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            print(e)
        else:
            return schema(**data) if schema is not None else data
    return schema() if schema is not None else None
    