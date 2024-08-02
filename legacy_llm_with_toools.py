import json
import langchain_core
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain.schema.runnable import RunnableLambda
from langchain_core.messages.ai import AIMessage

prompt = ChatPromptTemplate.from_template("{subject}")

def extract_llm_response(llm_response):
    print(f"{llm_response=}")
    if  isinstance(llm_response, AIMessage):
        _llm_response = json.loads(llm_response.content.replace("json","").replace("\n","").replace("`",""))
    else:
        _llm_response = llm_response["message"]["content"][llm_response["message"]["content"].index('{'):]
    if _llm_response:
        tool_and_data = _llm_response
        tool = tool_and_data["name"]
        parameters = tool_and_data["parameters"]
        result = langchain_core.agents.AgentActionMessageLog(tool=tool, tool_input=parameters, log=f"\nInvoking {tool} with `{parameters}`", message_log=[])
        return result
    langchain_core.agents.AgentActionMessageLog(tool=None, tool_input=None, log=llm_response, message_log=[llm_response])
    return result

extract_llm_response_runnable = RunnableLambda(extract_llm_response)

model_p = ChatOllama(
    model="phi3",
    temperature=0,
    )
chain = prompt | model_p | extract_llm_response
input = "Jane was born in 1986, what is jane`s age"
input = "help me troubleshoot nat on a cisco device with ip address 192.168.15.254"
subject = '''
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
             'date_of_birth': {
               'type': 'string',
               'description': 'Person`s date of birth',
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
result = chain.invoke(subject)
print(result)
