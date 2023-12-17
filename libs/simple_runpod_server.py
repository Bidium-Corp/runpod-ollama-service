# *************************************************************************** #
#                                                                              #
#    simple_runpod_server.py                                                   #
#                                                                              #
#    By: Widium <ebennace@student.42lausanne.ch>                               #
#    Github : https://github.com/widium                                        #
#                                                                              #
#    Created: 2023/12/11 16:10:27 by Widium                                    #
#    Updated: 2023/12/11 16:10:27 by Widium                                    #
#                                                                              #
# **************************************************************************** #

import json
import runpod
from typing import Any, Literal
from pydantic import BaseModel
import requests

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

def request_ollama_model(job : HandlerJob):
    
    base_url = "http://0.0.0.0:11434"
    input = job["input"]
    method_name = input["method_name"]
    parameters = input["parameters"]
    
    parameters["stream"] = False # We don't want to stream the output

    response = requests.post(
        url=f"{base_url}/api/{method_name}/",
        headers={"Content-Type": "application/json"},
        json=parameters,
    )
    response.encoding = "utf-8"

    return response.json()

# ---------------------------------------------------------------------------- #
#                       RunPod Serverless Handler                              #
# ---------------------------------------------------------------------------- #

def handler(job : HandlerJob):
    """
    This is the handler function that will be called by RunPod serverless.
    """
    response = request_ollama_model(job)
    answer = response["response"]
    
    return (answer)


if __name__ == '__main__':
    runpod.serverless.start({'handler': handler})