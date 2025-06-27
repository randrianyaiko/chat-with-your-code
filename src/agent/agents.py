from src.llms.google import model
from src.vectorDB.vectordb import VectorStore
from langchain_core.tools import Tool
from langchain.hub import pull
from langchain.agents import create_react_agent,AgentExecutor

class Agents:
    def __init__(self, vector_store:VectorStore, codebasetree:None|str=""):
        if codebasetree is None:
            self.codebasetree = "The project has no code base provided"
        else:
            self.codebasetree = f"This is my project codebase pulled from github : {codebasetree}"
        
        self.agent_prompt = pull("hwchase17/react")
        self.search_tool = Tool(
                name="search",
                func=vector_store.searchAndFormat,
                description="Searches the code base for relevant information."
            )

        self.vector_store = vector_store
        self.writter_agent = create_react_agent(
                                    #name="writter_agent",
                                    llm=model,
                                    tools=[self.search_tool],
                                    prompt=self.agent_prompt       
                                )
        
        self.writter_agent = AgentExecutor(
            agent=self.writter_agent,
            tools=[self.search_tool]
            )
                
        self.chat_history = []
        self.summary = ""
    
    def run(self, input_text:str, content_type:str="Documentation"):
        input_text = f"{self.codebasetree}\n\n{input_text}\n\n.The goal of the whole chat is to have a {content_type} content type.\n\n"
        input = {"input": input_text}
        self.chat_history.append(input)
        input = {"input": input_text+ f"\n\nChat History:{self.chat_history}"}
        response = self.writter_agent.invoke(input)
        self.chat_history.append(response)
        return response['output']
    
    