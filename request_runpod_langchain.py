# *************************************************************************** #
#                                                                              #
#    langchain_test.py                                                         #
#                                                                              #
#    By: Widium <ebennace@student.42lausanne.ch>                               #
#    Github : https://github.com/widium                                        #
#                                                                              #
#    Created: 2023/12/10 00:17:16 by Widium                                    #
#    Updated: 2023/12/10 00:17:16 by Widium                                    #
#                                                                              #
# **************************************************************************** #

import time
import json
import requests
from typing import Any, List, Mapping, Optional

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM

# ============================================================================= #

class RunpodServerlessLLM(LLM):
    
# ============================================================================= #

    pod_id: str
    api_key: str
    request_ids: List[str] = []
    difference_happen: bool = False

# ============================================================================= #

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"pod_id": self.pod_id}
    
    @property
    def _llm_type(self) -> str:
        return "runpod_serverless"

# ============================================================================= #

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if stop is not None and self._current_job_id is not None:
            #TODO: handle stop sequence
            ...
        
        stream = kwargs.get("stream")
        
        response = self._initiate_request(prompt, stream=stream)
        id = response.json()["id"]
        
        if stream == True:
            answer = self._handle_streaming_response(id)
        else :
            answer = self._handle_simple_response(id)
            
        if self.difference_happen == True:
            print(f"Difference happend ? {self.difference_happen}")
        
        return (answer)

# ============================================================================= #

    def _handle_streaming_response(self, id: str) -> str:
        
        status = self._get_status(id)["status"]
        
        full_output = ""
        while True:
            
            status = self._get_status(id)["status"]
            
            if status == "IN_QUEUE":
                print(f"REQUEST STATUS: {status}")
                time.sleep(1)
                
            if status == "IN_PROGRESS":
                full_output += self._process_stream(id)
                
            elif status == "COMPLETED":
                break
            
            elif status == "FAILED":
                raise ValueError("Request failed during execution.")
        
        # is completed
        securized_output = self._finalize_output(id, full_output)
        return securized_output

# ============================================================================= #

    def _handle_simple_response(self, id: str) -> str:
        
        status = self._get_status(id)["status"]
        
        while status != "COMPLETED":
            
            status = self._get_status(id)["status"]
            
            if status == "IN_QUEUE":
                print(f"REQUEST STATUS: {status}")
                time.sleep(1)
                
            elif status == "COMPLETED":
                break
            
            elif status == "FAILED":
                raise ValueError("Request failed during execution.")
            
        response = requests.get(
            f"{self._request_url()}/status/{id}",
            headers=self._request_headers(),
        )
        
        response.raise_for_status()
        answer = response.json()["output"]
        answer = "".join(answer)
                    
        return answer

# ============================================================================= #

    def _initiate_request(self, prompt: str, stream: bool) -> requests.Response:
        
        headers = self._request_headers()
        input_data = self._prepare_input(prompt, stream)
        
        response = requests.post(
            f"{self._request_url()}/run",
            headers=headers,
            json={"input": input_data},
            stream=stream
        )
        
        if response.status_code != 200:
            raise ValueError(f"Request failed with status code {response.status_code}")
        
        return response

# ============================================================================= #

    def _request_headers(self) -> Mapping[str, str]:
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": self.api_key,
        }

# ============================================================================= #

    def _request_url(self) -> str:
        return f"https://api.runpod.ai/v2/{self.pod_id}"

# ============================================================================= #

    def _prepare_input(self, prompt: str, stream: bool) -> Mapping[str, Any]:
        return {
            "method_name": "generate",
            "input": {
                "model": "mistral",
                "prompt": prompt,
                "stream": stream,
            },
        }
    
# ============================================================================= #

    def _get_status(self, id: str) -> Mapping[str, Any]:
        
        reponse = requests.get(
            f"{self._request_url()}/status/{id}",
            headers=self._request_headers(),
        ).json()
        
        return (reponse)

    
# ============================================================================= #

    def _process_stream(self, id: str) -> str:
        
        output = ""
        
        stream_response = requests.get(
            f"{self._request_url()}/stream/{id}",
            headers=self._request_headers(),
            stream=True
        )
        
        stream_response.raise_for_status()
        
        for line in stream_response.iter_lines():
            
            if line:
                part = json.loads(line.decode('utf-8'))
                
                for word in part["stream"]:
                    print(word["output"], end='', flush=True)
                    output += word["output"]
                    
        return output

# ============================================================================= #

    def _finalize_output(
        self,
        id: str,
        current_answer: str,
    ) -> str:
        """
        Secure the final output and print the difference if any.
        """
        final_response = self._get_status(id)
        
        updated_answer = self.update_and_print_difference(
            current_answer, 
            final_response["output"],
        )
        
        return updated_answer

# ============================================================================= #

    def update_and_print_difference(
        self,
        original : str, 
        tokens : List[str],
    ) -> str :
        
        final_str = ''.join(tokens)

        for i in range(min(len(original), len(final_str))):
            if original[i] != final_str[i]:
                difference_index = i
                break
        else:
            difference_index = len(original)  # If no difference is found till the minimum length

        # Extract and print the difference
        difference = final_str[difference_index:]

        if difference:
            self.difference_happen = True 
            print(difference, end="", flush=True)

        return final_str

# ============================================================================= #

from dotenv import load_dotenv
import os

load_dotenv()

# Access variables
POD_ID = os.environ["RUNPOD_POD_ID"]
RUNPOD_API_KEY = os.environ["RUNPOD_API_KEY"]

llm = RunpodServerlessLLM(
    pod_id=POD_ID,
    api_key=RUNPOD_API_KEY,
)

answer = llm(
    prompt="Tell me story in 6 words.", 
    stream=True,
)

print(f"\nANSWER: {answer}")



