from typing import Annotated, TypedDict
from dotenv import load_dotenv, find_dotenv

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

load_dotenv(find_dotenv())
llm_name = "gpt-3.5-turbo"

model = ChatOpenAI(model=llm_name)

from langgraph.graph.message import add_messages

BOT_NODE = "bot"
USER_INPUT_NODE = "user"

class State(TypedDict):
    messages: Annotated[list, add_messages]

def user_input(state: State):
    # print(f"State in user node : {state['messages']}")
    user = input("User: ")
    return {"messages": [("user", user)]}

def should_continue(state: State):
    last_message = state['messages'][-1].content
    if last_message.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        return END
    return BOT_NODE

def bot(state: State):
    # print(f"State in bot node : {state['messages']}")
    res = model.invoke(state["messages"])
    ai_message = res.content
    print(ai_message)
    return {"messages": [("ai", ai_message)]}

graph_builder = StateGraph(State)

graph_builder.add_node(USER_INPUT_NODE, user_input)
graph_builder.add_node(BOT_NODE, bot)

graph_builder.set_entry_point(USER_INPUT_NODE)
graph_builder.add_conditional_edges(USER_INPUT_NODE, should_continue, {
    BOT_NODE: BOT_NODE,
    END: END
})
graph_builder.add_edge(BOT_NODE, USER_INPUT_NODE)

graph = graph_builder.compile()
graph.get_graph().draw_mermaid_png(output_file_path="graph.png")

graph.invoke({"messages": [("system", "You are a chatbot that refers to previous user messages to ensure context-aware"
                                      " and seamless responses. Use the message history to maintain continuity and avoid"
                                      " repetition or missed details.")]})
