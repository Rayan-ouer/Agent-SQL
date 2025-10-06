import os
from app.prompt import system_prompt
from dotenv import load_dotenv
from langchain import hub
from sqlalchemy.dialects.mysql import base
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit, QuerySQLDataBaseTool, InfoSQLDatabaseTool, ListSQLDatabaseTool
from app.utils import create_engine_for_sql_database, patched_correct_for_mysql_bugs

load_dotenv()

def init_engine() -> SQLDatabase:
    base.MySQLDialect._correct_for_mysql_bugs_88718_96365 = patched_correct_for_mysql_bugs
    engine = create_engine_for_sql_database("mysql+pymysql:")
    return SQLDatabase(engine=engine)

def init_prompt(diaclect_db: str) -> str:
    prompt_template = ChatPromptTemplate.from_messages([("system", system_prompt)])
    print(prompt_template.messages)
    assert len(prompt_template.messages) == 1
    return prompt_template.format(dialect=diaclect_db, top_k=5)

def create_agent_az():
    db = init_engine()

    api_key = os.getenv("API_KEY_GROK")
    if not api_key:
        raise RuntimeError("La clé API GROQ est manquante dans l'environnement")
    os.environ["GROQ_API_KEY"] = api_key

    llm = init_chat_model("llama-3.3-70b-versatile", model_provider="groq")
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    system_message = init_prompt("MYSQL")
    return create_react_agent(llm, toolkit.get_tools(), prompt=system_message)