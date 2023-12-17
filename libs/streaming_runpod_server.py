# *************************************************************************** #
#                                                                              #
#    streaming_runpod.py                                                       #
#                                                                              #
#    By: Widium <ebennace@student.42lausanne.ch>                               #
#    Github : https://github.com/widium                                        #
#                                                                              #
#    Created: 2023/12/11 13:19:33 by Widium                                    #
#    Updated: 2023/12/11 13:19:33 by Widium                                    #
#                                                                              #
# **************************************************************************** #

import json
import runpod
from typing import Any, Literal, TypedDict, AsyncGenerator
from pydantic import BaseModel
import requests
import asyncio

# ---------------------------------------------------------------------------- #
#                               Input Json Typing                              #
# ---------------------------------------------------------------------------- #

class Parameters(BaseModel):
    model: str
    prompt: str
    stream: bool

class HandlerInput(BaseModel):
    method_name: Literal["generate"]
    input: Parameters

class HandlerJob(BaseModel):
    input: HandlerInput

# Typical Input Json :
# {
#   "input": {
#     "method_name": "generate",
#     "parameters": {
#       "prompt": "Tell me a fairytail story",
#       "model" : "mistral",
#       "stream": true
#     }
#   }
# }


# ---------------------------------------------------------------------------- #
#                         Ollama Request Function                              #
# ---------------------------------------------------------------------------- #

async def request_ollama_model(job: HandlerJob) -> AsyncGenerator[str, None]:
    
    base_url = "http://0.0.0.0:11434"
    input = job["input"]
    method_name = input["method_name"]
    parameters = input["parameters"]
    
    response = requests.post(
        url=f"{base_url}/api/{method_name}/",
        headers={"Content-Type": "application/json"},
        json=parameters,
        stream=True,
    )
    response.encoding = "utf-8"
    
    # Process the response as a stream
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            json_data = json.loads(decoded_line)
            token = json_data["response"]
            yield token
            await asyncio.sleep(0)  # Allow other tasks to run

# ---------------------------------------------------------------------------- #
#                       RunPod Serverless Handler                              #
# ---------------------------------------------------------------------------- #

async def generator_handler(job: HandlerJob) -> AsyncGenerator[str, None]:
    """
    This is the handler function that will be called by RunPod serverless.
    """   
    async for response in request_ollama_model(job):
        yield response

if __name__ == '__main__':
    runpod.serverless.start(
        {
            'handler': generator_handler,
            "return_aggregate_stream": True,
        }
    )