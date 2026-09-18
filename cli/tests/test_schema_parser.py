from mcp_client.schema_parser import (
    ToolParameter,
    cast_parameter_value,
    parse_tool_parameters,
)


def test_parse_dnstool_schema():
    # User's exact example schema
    schema = {
        "additionalProperties": False,
        "properties": {
            "hostname": {
                "type": "string",
                "description": "Hostname/ip or ldap://host:port connection string to connect to.",
            },
            "action": {
                "enum": ["add", "modify", "query", "remove", "ressurrect", "ldapdelete"],
                "type": "string",
                "description": "Action to perform.",
            },
            "username": {
                "type": "string",
                "description": "Domain\\username for authentication.",
            },
            "password": {
                "type": "string",
                "description": "Password or LM:NTLM hash for authentication.",
            },
            "zone": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "default": None,
                "description": "DNS zone to search in.",
            },
            "record": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "default": None,
                "description": "DNS record to target FQDN.",
            },
            "record_data": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "default": None,
                "description": "Record value.",
            },
            "use_kerberos": {
                "default": False,
                "type": "boolean",
                "description": "Use Kerberos authentication (-k).",
            },
            "extra_args": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "default": None,
                "description": "Additional arguments.",
            },
            "timeout": {
                "default": 120,
                "type": "integer",
                "description": "Max execution time in seconds.",
            },
        },
        "required": ["hostname", "action", "username", "password"],
        "type": "object",
    }

    params = parse_tool_parameters(schema)
    param_map = {p.name: p for p in params}

    # Verify required parameters
    assert param_map["hostname"].is_required is True
    assert param_map["action"].is_required is True
    assert param_map["username"].is_required is True
    assert param_map["password"].is_required is True

    # Verify optional parameters with defaults / anyOf
    assert param_map["use_kerberos"].is_required is False
    assert param_map["use_kerberos"].default is False
    assert param_map["use_kerberos"].param_type == "boolean"

    assert param_map["timeout"].is_required is False
    assert param_map["timeout"].default == 120
    assert param_map["timeout"].param_type == "integer"

    assert param_map["zone"].is_nullable is True
    assert param_map["zone"].default is None

    # Verify enum detection
    assert param_map["action"].enum_values == [
        "add",
        "modify",
        "query",
        "remove",
        "ressurrect",
        "ldapdelete",
    ]


def test_cast_parameter_value_string_required():
    param = ToolParameter(name="hostname", param_type="string", description="", is_required=True)
    val, err = cast_parameter_value(param, "dc01.corp.local")
    assert err is None
    assert val == "dc01.corp.local"

    # Empty required string
    val, err = cast_parameter_value(param, "")
    assert err is not None
    assert "required" in err


def test_cast_parameter_value_enum():
    param = ToolParameter(
        name="action",
        param_type="string",
        description="",
        is_required=True,
        enum_values=["add", "modify", "query"],
    )

    # By string
    val, err = cast_parameter_value(param, "add")
    assert err is None
    assert val == "add"

    # By number index (1-based)
    val, err = cast_parameter_value(param, "2")
    assert err is None
    assert val == "modify"

    # Invalid choice
    val, err = cast_parameter_value(param, "invalid_action")
    assert err is not None
    assert "Allowed values" in err


def test_cast_parameter_value_boolean():
    param = ToolParameter(name="use_kerberos", param_type="boolean", description="", is_required=False, default=False)

    val, err = cast_parameter_value(param, "true")
    assert err is None and val is True

    val, err = cast_parameter_value(param, "yes")
    assert err is None and val is True

    val, err = cast_parameter_value(param, "0")
    assert err is None and val is False

    # Empty input should return default
    val, err = cast_parameter_value(param, "")
    assert err is None and val is False


def test_cast_parameter_value_integer():
    param = ToolParameter(name="timeout", param_type="integer", description="", is_required=False, default=120)

    val, err = cast_parameter_value(param, "60")
    assert err is None and val == 60

    # Default on empty
    val, err = cast_parameter_value(param, "")
    assert err is None and val == 120

    # Invalid int
    val, err = cast_parameter_value(param, "not_a_number")
    assert err is not None


def test_cast_parameter_value_nullable():
    param = ToolParameter(name="zone", param_type="string", description="", is_required=False, default=None, is_nullable=True)

    val, err = cast_parameter_value(param, "")
    assert err is None and val is None

    val, err = cast_parameter_value(param, ":null")
    assert err is None and val is None

    val, err = cast_parameter_value(param, "corp.local")
    assert err is None and val == "corp.local"
