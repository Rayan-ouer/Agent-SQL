import logging
from app.agent import create_agent_az
from app.model import Question
from fastapi import FastAPI, HTTPException, Response, status
from langgraph.errors import GraphRecursionError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    )

def initializeModel():
    app = FastAPI(
        title="NegoBot Model API",
        description="Model NLP for Nego bot",
        version="0.1",
    )

    async def startup_event():
        try:
            app.state.agent_executor = create_agent_az()
        except Exception as e:
            logging.error(f"Erreur à l'initialisation de l'agent : {e}")
            raise RuntimeError("Échec de l'initialisation du modèle")
    
    app.add_event_handler("startup", startup_event)
    return app

app = initializeModel()

RECURSION_LIMIT = (3 * 5 + 1)

@app.post("/predict", status_code=200)
async def callBot(question: Question, response: Response):
    final_message = None
    try:
        events = app.state.agent_executor.stream(
            {"messages": [("user", question.question)]},
            {"recursion_limit": RECURSION_LIMIT},
            stream_mode="values",
        )
        for event in events:
            messages = event.get("messages", [])
            if messages:
                final_message = messages[-1]
            print(final_message)
        return {
            "status": "success",
            "response": str(final_message.content)
        }
    except GraphRecursionError:
        return {
            "status": "error",
            "response": "Agent stoppé : nombre maximal d'itérations atteint."
        }
