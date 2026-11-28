import inspect
import types
from typing import Annotated, Any, Callable
from typing import Annotated, Union, get_args, get_origin, get_type_hints

from pydantic import BaseModel, Field



def get_current_weather(location: Annotated[str, "城市或县区，比如北京市、杭州市、余杭区等。"]):
    '''
      当你想查询指定城市的天气时非常有用。
    '''
    return f"当前{location}的天气是晴朗的，温度为25摄氏度。"


functions_map: dict[str, Callable[..., Any]] = {
  "get_current_weather": get_current_weather
}


JSON_TYPES = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


def build_param_schema(annotation) -> dict:
  """把 Python 类型注解转成 JSON Schema 片段。"""
  origin = get_origin(annotation)

  # Annotated[str, "说明"] -> {"type": "string", "description": "说明"}
  if origin is Annotated:
    base, *metadata = get_args(annotation)
    schema = build_param_schema(base)
    for item in metadata:
      if isinstance(item, str) and "description" not in schema:
        schema["description"] = item
    return schema

  # Optional[str] / Union[str, int]
  if origin in (Union, types.UnionType):
    args = [arg for arg in get_args(annotation) if arg is not type(None)]
    if len(args) == 1:
      return build_param_schema(args[0])
    return {"anyOf": [build_param_schema(arg) for arg in args]}

  # list[str] / tuple[int, ...]
  if origin in (list, tuple, set):
    args = get_args(annotation)
    schema = {"type": "array"}
    if args:
      schema["items"] = build_param_schema(args[0])
    return schema

  if origin is dict:
    return {"type": "object"}

  return {"type": JSON_TYPES.get(annotation, "string")}


def get_function_tools() -> list[dict]:
  '''
    获取工具列表
  '''
  result = []
  for fn_name, fn in functions_map.items():
    # include_extras=True 才能拿到 Annotated 里的描述
    hints = get_type_hints(fn, include_extras=True)
    signature = inspect.signature(fn)

    properties = {}
    required = []
    for name, param in signature.parameters.items():
      if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
        continue
      properties[name] = build_param_schema(hints.get(name, str))
      if param.default is inspect.Parameter.empty:
        required.append(name)

    result.append({
      "type": "function",
      "name": fn_name,
      "description": inspect.getdoc(fn) or "",
      "parameters": {
        "type": "object",
        "properties": properties,
        "required": required,
      },
    })

  return result

