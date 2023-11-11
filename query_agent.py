import os
import autogen
from query_agent_tool import VectaraQueryTool
# from autogen import AssistantAgent, UserProxyAgent, config_list_from_json, config_list_from_env

from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
import streamlit as st

# Define the config_list

# config_list = autogen.config_list_from_json(
#     env_or_file="OAI_CONFIG_LIST",  # or OAI_CONFIG_LIST.json if file extension is added
#     filter_dict={
#         "model": {
#             # "gpt-4",
#             # "gpt-3.5-turbo",
#             "gpt-3.5-turbo-16k"
#         }
#     }
# )

# config_list = autogen.confi

# config_list = autogen.config_list_from_env()

# config_list = autogen.config_list_from_json(
#     env_or_file=".env",  # or OAI_CONFIG_LIST.json if file extension is added
#     filter_dict={
#         "model": {
#             # "gpt-4",
#             # "gpt-3.5-turbo",
#             "gpt-3.5-turbo-16k"
#         }
#     }
# )

    # llm_config = {
    #     "request_timeout": 600,
    #     "config_list": [
    #         {
    #             "model": selected_model,
    #             "api_key": selected_key
    #         }
    #     ]
    # }

selected_model = None
selected_key = None
with st.sidebar:
    st.header("OpenAI Configuration")
    selected_model = st.selectbox("Model", ['gpt-3.5-turbo', 'gpt-4'], index=1)
    selected_key = st.text_input("API Key", type="password")

# Define a function to generate llm_config from a LangChain tool
def generate_llm_config(tool):
    # Define the function schema based on the tool's args_schema
    function_schema = {
        "name": tool.name.lower().replace (' ', '_'),
        "description": tool.description,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }

    if tool.args is not None:
      function_schema["parameters"]["properties"] = tool.args

    return function_schema


custom_tool = VectaraQueryTool()

# Construct the llm_config
llm_config = {
  #Generate functions config for the Tool
  "functions":[
      generate_llm_config(custom_tool),

  ],
#   "config_list": config_list,  # Assuming you have this defined elsewhere
  "timeout": 120,
  "request_timeout": 600,
        "config_list": [
            {
                "model": selected_model,
                "api_key": selected_key
            }
        ]
}
openai_api_key = llm_config["config_list"][0]["api_key"]

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "coding"},
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    # is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", "").rstrip(),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "coding"},
)

# Register the tool and start the conversation
user_proxy.register_function(
    function_map={
        custom_tool.name: custom_tool._run,
    }
)

chatbot = autogen.AssistantAgent(
    name="chatbot",
    # system_message="For coding tasks, only use the functions you have been provided with. Reply TERMINATE when the task is done.",
    # system_message="After providing the answer, please reply TERMINATE to end the conversation.",
    system_message="After providing the answer, please end the conversation. Make sure to include the word TERMINATE in your message.",
    llm_config=llm_config,

)


def user_generated_query(user_query) -> str:

    user_proxy.initiate_chat(
    chatbot,
    message= f"""a user will query vectara with the following query: {user_query}
you must use this query to use vectara and please provide feeback to the user as to how they can produce a better response. 
If the query is high quality then compliment them on it. Also give the user a sample query that could protentally provide them with a good output""" + user_query, 
   llm_config=llm_config,

)
    return chatbot.last_message()['content']

# if __name__ == "__main__":
# #    user_generated_query("What is the overall sentiment in the data?")
#     data = user_generated_query("What does the document contain pertaining to pets?")
#     print(data)

st.title("💬 Chatbot") 

with st.sidebar:
    # openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/isayahc/Tax-Team/blob/streamlit/query_agent.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    with st.spinner('Processing...'):

        data = user_generated_query(prompt)
        # msg = response.choices[0].message
        # msg = data
        # st.session_state.messages.append(msg)
        # st.chat_message("assistant").write(msg.content)
        st.write(data)
