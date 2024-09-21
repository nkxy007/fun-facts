import json
import langchain_core
from langchain.schema.agent import AgentFinish, AgentActionMessageLog
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain.schema.runnable import RunnableLambda
from langchain_core.messages.ai import AIMessage
import paramiko
import requests
import datetime
from typing import List

# define credentials
username = "username"
password = "super-secret-password"

# Defining tools
def  get_current_weather(city: str):
    '''Function to get the weather information'''
    url = f"http://wttr.in/{city}?format=%C+%t+%h+%w"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.strip()
    else:
        return f"Error: Unable to get weather data for {city}"

def calculate_people_age(year_of_birth: str):
    age = datetime.datetime.now().year - int(year_of_birth)
    return age

def connect_to_the_device(device_ip_address: str, commands: List[str]):
    output = []
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(device_ip_address, username=username, password=password, timeout=4)
        for command in commands:
            stdin, stdout, stderr = ssh.exec_command(command)
            output.append(stdout.read().decode())
    except Exception as e:
        print(f"failed with exception {e} - {device_ip_address}")
    ssh.close()
    return output


prompt = ChatPromptTemplate.from_template("{subject}")


def extract_llm_response(llm_response):
    # Need to craft different data models for the basic LLM. This function is not needed
    # when you run a tool aware LLM like llama3.1 or openAI and Anthropic SOTA LLMs
    print(f"{llm_response=}")
    _llm_response = None
    if  isinstance(llm_response, AIMessage):
        try:
            _llm_response = json.loads(llm_response.content.replace("`","").replace("json","").replace("\n","").replace("`",""))
        except Exception as e:
            print(f"encountered error {e} while decoding LLM message")
    else:
        _llm_response = llm_response["message"]["content"][llm_response["message"]["content"].index('{'):]
    if _llm_response:
        tool_and_data = _llm_response
        tool = tool_and_data["name"]
        parameters = tool_and_data["parameters"]
        result = AgentActionMessageLog(tool=tool, tool_input=parameters, log=f"\nInvoking {tool} with `{parameters}`", message_log=[])
        return result
    # langchain_core.agents.AgentActionMessageLog(tool=None, tool_input=None, log=llm_response, message_log=[llm_response])
    result = AgentFinish(
        return_values={'output': llm_response}, 
        log=_llm_response
    )
    return result

extract_llm_response_runnable = RunnableLambda(extract_llm_response)

model_p = ChatOllama(
    model="phi3",
    temperature=0,
    )
input = "Jane was born in 1986, what is jane`s age"
input = "help me troubleshoot nat on a cisco device with ip address 192.168.15.254"
subject = '''
	    Given the following functions, if a function is applicable to the question, please respond with a JSON for a function call with its proper arguments that best answers the given prompt.

        Respond in the format {"name": function name, "parameters": dictionary of argument name and its value}. Do not use variables. If no function applicable, 
		respond to the question the way you deem correct like hi or how can I help you.
		[
	{'type': 'function',
      'function': {
        'name': 'calculate_people_age',
        'description': 'Clculate a person`s age',
        'parameters': {
          'type': 'object',
          'properties': {
            'year_of_birth': {
              'type': 'string',
              'description': 'Person`s year of birth',
            },
          },
          'required': ['date_of_birth'],
        },
      },
    },
	{'type': 'function',
      'function': {
        'name': 'connect_to_the_device',
        'description': 'connect to the devices and run commands',
        'parameters': {
          'type': 'object',
          'properties': {
            'device_ip_address': {
              'type': 'string',
              'description': 'device`s IP address',
            },
			'commands': {
              'type': 'list',
              'description': 'a list of commands to run',
            },
          },
          'required': ['device_ip_address', 'commands'],
        },
      },
    },
	]
		
        ''' + input

# defining a loop with a routing mechanism that can determine what tool to call
def route(result):
    if isinstance(result, AgentFinish):
        return result.return_values['output']
    else:
        tools = {
            "calculate_people_age": calculate_people_age,
            "connect_to_the_device": connect_to_the_device
        }
        tool_run_result = tools[result.tool](**result.tool_input)
        # call llm with input
        extra = " .do not propose any other tool ot anything else format the answer to human friendly format"
        _input = f"{input} and tool called was {result.tool} and result is {tool_run_result}" + extra
        _chain = prompt | model_p
        _result = _chain.invoke(_input)
        return _result.content

# call the executte tool
chain = prompt | model_p | extract_llm_response | route
final_result = chain.invoke(subject)
print(f"final result is: {final_result}")
