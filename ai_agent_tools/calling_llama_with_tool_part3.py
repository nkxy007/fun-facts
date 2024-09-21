# This scripts calls LLm like LLama3.1 that is tool aware 
import paramiko
import datetime
import requests
from typing import List
from langchain.tools import tool
from langchain.prompts import MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent#

username = 'user'
password = 'hard-to-know'
model_name = "llama3.1"

# define tools
@tool
def  get_current_weather(city: str) -> str:
    '''Function to get the weather information of any given city'''
    url = f"http://wttr.in/{city}?format=%C+%t+%h+%w"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.strip()
    else:
        return f"Error: Unable to get weather data for {city}"

@tool
def calculate_people_age(year_of_birth: str) ->str:
    """Function to calculate age based on the year of birth"""
      
    age = datetime.datetime.now().year - int(year_of_birth)
    age_as_text = f"the age is {age}"
    return age_as_text

@tool
def connect_to_the_device(device_ip_address: str, commands_list: List[str]):
    """Function that connect to the device and runs a series of commands"""
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


tools = [get_current_weather, calculate_people_age, connect_to_the_device]


system_prompt = "you are a savvy and helpful assistant "

# define the prompt template
prompt = ChatPromptTemplate.from_messages(
    [
    ("system", system_prompt),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
    ]
)

# config LLM parameters
llm = ChatOllama (
    model=model_name,
    temperature=0,
).bind_tools(tools=tools)

input = "help me troubleshoot nat on a cisco device with ip address 192.168.15.254"
input = "Bob was born in 1985, what is jane age, return the tool to call"
#input = "what is the weather like in Sydney Australia?"

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
agent_executor.invoke({"input": input})
