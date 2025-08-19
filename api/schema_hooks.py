"""
OpenAPI post-processing hooks for drf-spectacular.

This module customizes the generated schema so that any query parameter named
"ordering" (coming from DRF's OrderingFilter) is represented as an enum with
values "asc" and "desc".
"""

from typing import Any, Dict


def set_ordering_enum(result: Dict[str, Any], generator: Any, request: Any, public: bool) -> Dict[str, Any]:
    """
    Replace schema for query parameter named "ordering" with enum ["asc", "desc"].

    This is applied across all paths/operations that include the parameter.
    """
    enum_schema = {"type": "string", "enum": ["asc", "desc"]}

    # First update any reusable component parameters named 'ordering'
    try:
        components_params = result.get("components", {}).get("parameters", {})
        for _param_key, comp_param in components_params.items():
            if isinstance(comp_param, dict) and comp_param.get("name") == "ordering" and comp_param.get("in") == "query":
                comp_param["schema"] = dict(enum_schema)
    except Exception:
        pass

    # Then update inline/operation parameters or $ref to component params
    paths = result.get("paths", {})
    for _path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for _method, operation in methods.items():
            if not isinstance(operation, dict):
                continue
            parameters = operation.get("parameters", [])
            if not isinstance(parameters, list):
                continue
            for param in parameters:
                # Inline parameter
                if isinstance(param, dict) and param.get("name") == "ordering" and param.get("in") == "query":
                    param["schema"] = dict(enum_schema)
                    continue
                # Parameter by $ref
                if isinstance(param, dict) and "$ref" in param and isinstance(param["$ref"], str):
                    ref = param["$ref"]
                    if ref.startswith("#/components/parameters/"):
                        key = ref.split("/")[-1]
                        comp_param = result.get("components", {}).get("parameters", {}).get(key)
                        if isinstance(comp_param, dict) and comp_param.get("name") == "ordering" and comp_param.get("in") == "query":
                            comp_param["schema"] = dict(enum_schema)
    return result


