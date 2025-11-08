# RUN ONCE AT PROJECT RUN
import os

import psycopg
from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver

load_dotenv()

database_url = os.getenv("DATABASE_URL")
database_url = database_url.replace("postgresql+psycopg://", "postgresql://")

conn = psycopg.connect(database_url, autocommit=True)
checkpointer = PostgresSaver(conn=conn)
checkpointer.setup()
