import json
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolParameter:
    name: str
    param_type: str
    description: str
    is_required: bool
    default: Any = None
    enum_values: list[Any] | None = None
    is_nullable: bool = False

    @property
    def type_display(self) -> str:
        parts = [self.param_type]
        if self.is_nullable:
            parts.append("optional")
        if self.enum_values:
            parts.append(f"enum({len(self.enum_values)})")
        return "/".join(parts)


def get_tool_schema(tool: Any) -> dict[str, Any]:
    """Extract a JSON schema dict from a LangChain BaseTool."""
    args_schema = getattr(tool, "args_schema", None)
    if args_schema is not None:
        if isinstance(args_schema, dict):
            return args_schema
        if hasattr(args_schema, "model_json_schema"):
            return args_schema.model_json_schema()
        if hasattr(args_schema, "schema"):
            return args_schema.schema()

    args = getattr(tool, "args", None)
    if isinstance(args, dict):
        required_list = []
        for prop_name, prop_spec in args.items():
            if isinstance(prop_spec, dict):
                has_default = "default" in prop_spec
                any_of = prop_spec.get("anyOf", [])
                is_nullable = any(x.get("type") == "null" for x in any_of)
                if not has_default and not is_nullable:
                    required_list.append(prop_name)

        return {
            "type": "object",
            "properties": args,
            "required": required_list,
        }

    return {}


def parse_tool_parameters(schema: dict[str, Any]) -> list[ToolParameter]:
    """Parse JSON schema properties into a list of ToolParameter objects, sorted required first."""
    properties = schema.get("properties", {})
    required_names = set(schema.get("required", []))
    parsed: list[ToolParameter] = []

    for name, info in properties.items():
        if not isinstance(info, dict):
            continue

        description = info.get("description", "")
        default_val = info.get("default")
        enum_vals = info.get("enum")
        raw_type = info.get("type")
        is_nullable = False

        # Handle anyOf schemas (e.g. anyOf: [{'type': 'string'}, {'type': 'null'}])
        if "anyOf" in info:
            any_of = info["anyOf"]
            types = [t.get("type") for t in any_of if isinstance(t, dict) and "type" in t]
            if "null" in types:
                is_nullable = True
                non_null_types = [t for t in types if t != "null"]
                raw_type = non_null_types[0] if non_null_types else "string"
            else:
                raw_type = types[0] if types else "string"

        # Normalize type string
        if not raw_type:
            raw_type = "string"

        is_req = (name in required_names) and (default_val is None) and (not is_nullable)

        param = ToolParameter(
            name=name,
            param_type=str(raw_type).lower(),
            description=description,
            is_required=is_req,
            default=default_val,
            enum_values=enum_vals,
            is_nullable=is_nullable,
        )
        parsed.append(param)

    # Sort required parameters first, then alphabetically
    parsed.sort(key=lambda p: (not p.is_required, p.name))
    return parsed


def cast_parameter_value(
    param: ToolParameter, raw_input: str
) -> tuple[Any, str | None]:
    """Cast a raw string input to the expected schema type.

    Returns:
        tuple[Any, str | None]: (cast_value, error_message). If error_message is None, casting succeeded.
    """
    cleaned = raw_input.strip()

    # Handle explicit null or empty input
    if cleaned in (":null", ":none"):
        if param.is_nullable or not param.is_required:
            return None, None
        return None, f"Parameter '{param.name}' is required and cannot be null."

    if not cleaned:
        if param.default is not None:
            return param.default, None
        if param.is_nullable or not param.is_required:
            return None, None
        return None, f"Parameter '{param.name}' is required."

    # Handle enum validation
    if param.enum_values:
        # Check if user entered an option number: 1, 2, ...
        if cleaned.isdigit():
            idx = int(cleaned) - 1
            if 0 <= idx < len(param.enum_values):
                return param.enum_values[idx], None

        # Check direct value match (case-insensitive where possible)
        for val in param.enum_values:
            if str(val).lower() == cleaned.lower():
                return val, None

        allowed = ", ".join(f"'{v}'" for v in param.enum_values)
        return None, f"Invalid choice '{cleaned}'. Allowed values: {allowed}"

    # Handle basic types
    ptype = param.param_type
    if ptype in ("integer", "int"):
        try:
            return int(cleaned), None
        except ValueError:
            return None, f"'{cleaned}' is not a valid integer."

    elif ptype in ("number", "float"):
        try:
            return float(cleaned), None
        except ValueError:
            return None, f"'{cleaned}' is not a valid number."

    elif ptype in ("boolean", "bool"):
        lower = cleaned.lower()
        if lower in ("y", "yes", "true", "t", "1"):
            return True, None
        if lower in ("n", "no", "false", "f", "0"):
            return False, None
        return None, f"'{cleaned}' is not a valid boolean. Enter true/false or y/n."

    elif ptype in ("array", "list"):
        # Try JSON array first
        if cleaned.startswith("[") and cleaned.endswith("]"):
            try:
                parsed = json.loads(cleaned)
                if isinstance(parsed, list):
                    return parsed, None
            except json.JSONDecodeError as e:
                return None, f"Invalid JSON array: {e}"
        # Fallback to comma-separated list
        return [item.strip() for item in cleaned.split(",") if item.strip()], None

    elif ptype in ("object", "dict"):
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                return parsed, None
            return None, "JSON input must be an object (dictionary)."
        except json.JSONDecodeError as e:
            return None, f"Invalid JSON object: {e}"

    # Default: string
    return cleaned, None
