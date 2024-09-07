# This scripts calls LLm like LLama3 or Phi3 that do not have any clue what is a tool
# or function and can determine which tool to use by using in-context learning
import ollama
import json
import paramiko
import datetime
import requests
from typing import List

username = 'user'
password = 'hard-to-know'

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

def connect_to_the_device(device_ip_address: str, commands_list: List[str]):
    output = []
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(device_ip_address, username=username, password=password, timeout=4)
        for command in commands_list:
            stdin, stdout, stderr = ssh.exec_command(command)
            output.append(stdout.read().decode())
    except Exception as e:
        print(f"failed with exception {e} - {device_ip_address}")
    ssh.close()
    return output

all_tools = {
  "get_current_weather": get_current_weather,
  "calculate_people_age": calculate_people_age,
  "connect_to_the_device": connect_to_the_device
}

input = "help me troubleshoot nat on a cisco device with ip address 192.168.15.254"
input = "jane was born in 1987, what is jane age"
model_name = 'phi3' # 'llama3'
response = ollama.chat(
    model= model_name,
    messages=[
	{'role': 'system','content':
	'''
	You are a helpful assistant with tool calling capabilities. When you receive a tool call response, use the output to format an answer to the orginal user question.
    '''
	},
	{'role': 'user', 'content': 
	     '''
	    Given the following functions, if a function is applicable to the question, please respond with a JSON for a function call with its proper arguments that best answers the given prompt.

        Respond in the format {"name": function name, "parameters": dictionary of argument name and its value}. Do not use variables. If no function applicable, 
		respond to the question the way you deem correct like hi or how can I help you.
		[{
      'type': 'function',
      'function': {
        'name': 'get_current_weather',
        'description': 'Get the current weather for a city',
        'parameters': {
          'type': 'object',
          'properties': {
            'city': {
              'type': 'string',
              'description': 'The name of the city',
            },
          },
          'required': ['city'],
        },
      },
    },
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
		}]
)
print(f'{response=}')
tool_and_data_str = response["message"]["content"][response["message"]["content"].index('{'):]
if tool_and_data_str:
    tool_and_data = json.loads(tool_and_data_str)
    print(f'{tool_and_data=}')
    tool = tool_and_data["name"]
    parameters = tool_and_data["parameters"]
    result = all_tools[tool](**parameters)
    # add result to context and call LLM again
    response = response = ollama.chat(
        model= model_name,
        messages=[
	    {'role': 'system','content':
	    '''
	    You are a helpful assistant with presenting results in human understandable way
        '''
	    },
	    {'role': 'user', 'content': 
	        '''Given the following result from a called function ''' + tool + '''with question: ''' + input + ''' here are the result: ''' + str(result) 
            }]
    )
    print(f'LLM Final answer: {response["message"]["content"]}')

print(f'LLM Final answer: {response["message"]["content"]}')
      

# Run llm again with results
