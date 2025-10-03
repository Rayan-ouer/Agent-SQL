import os
from dotenv import load_dotenv
import getpass

from sqlalchemy import create_engine, MetaData
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.chat_models import init_chat_model
from sqlalchemy.dialects.mysql import base
from langchain import hub
from langgraph.prebuilt import create_react_agent


load_dotenv()

def patched_correct_for_mysql_bugs(*args, **kwargs):
    pass

def create_engine_for_sql_database(connection_string: str):
    engine = create_engine(
            connection_string
            + os.getenv(("AI_USERNAME"))
            + ":"
            + os.getenv(("AI_PASSWORD"))
            + "@"
            + os.getenv(("DB_HOST"))
            + ":"
            + os.getenv(("DB_PORT"))
            + "/"
            + os.getenv(("DB_DATABASE"))
        )
    return engine

base.MySQLDialect._correct_for_mysql_bugs_88718_96365 = patched_correct_for_mysql_bugs

engine = create_engine_for_sql_database(connection_string="mysql+pymysql://")

db = SQLDatabase(engine=engine)

if not os.environ.get("GROQ_API_KEY"):
  os.environ["GROQ_API_KEY"] = os.getenv("API_KEY_GROK")

llm = init_chat_model("llama-3.3-70b-versatile", model_provider="groq")

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")

assert len(prompt_template.messages) == 1
print(prompt_template.input_variables)

system_message = prompt_template.format(dialect="MYSQL", top_k=5)

agent_executor = create_react_agent(llm, toolkit.get_tools(), prompt=system_message)

example_query = "Quel voiture nous rapporte le plus d'argent par sa vente de piece, donne moi le nom des pieces et le nom exacte de la voiture"

events = agent_executor.stream(
    {"messages": [("user", example_query)]},
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()