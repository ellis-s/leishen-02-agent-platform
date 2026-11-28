# import json
# import os
import inspect
import json
import types
from typing import Annotated, Union, get_args, get_origin, get_type_hints

import httpx2
from openai import OpenAI
from openai.types.beta.beta_response_input_item import FunctionCallOutput
from openai.types.responses import Response, ResponseFunctionToolCallItem, ResponseFunctionToolCallParam

from src.utils.tools import functions_map, get_function_tools

# 百炼平台的业务空间ID
workspace_id = "ws-yq3ond3ilk1rzs8z"

client = OpenAI(
  # api_key=os.getenv('OPENROUTER_API_KEY'),
  # base_url="https://openrouter.ai/api/v1"

  base_url=f"https://{workspace_id}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
  # http_client=httpx2.Client(
  #   proxy="http://127.0.0.1:9099",
  #   timeout=60.0
  # )
)


tools = get_function_tools()
functions = functions_map


def llm_call(messages) -> Response:
  response = client.responses.create(
      model="qwen3.8-max-0902",
      input=messages,
      tools=tools,
  )
  return response

messages = [
    # {
    #     "role": "system",
    #     "content": "你是一个中国天气查询小助手，你需要根据用户输入的城市名称，返回该城市的天气情况。"
    # },
    {
        "role": "user",
        "content": "北京天气如何？"
    }
]
response = llm_call(messages)

function_calls: list[Response] = [item for item in response.output if item.type == 'function_call']

count = 1

while function_calls:
  print(f"第{count}次调用 function tools!")
  count += 1
  for item in function_calls:
      name, call_id, arguments = item.name, item.call_id, item.arguments

      kwargs = json.loads(arguments or "{}")
      fn_res = functions[name](**kwargs)

      messages.append(ResponseFunctionToolCallParam(
        arguments=arguments,
        call_id=call_id,
        name=name,
        type='function_call',
      ))

      messages.append(FunctionCallOutput(
        output=fn_res,
        type='function_call_output',
        call_id=call_id,
      ))
  
  response = llm_call(messages)
  function_calls: list[Response] = [item for item in response.output if item.type == 'function_call']


print(f"最终输出: {response.output_text}")


   







