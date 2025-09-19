import os
from dotenv import load_dotenv
load_dotenv()

OMDB_API_KEY = os.environ["OMDB_API_KEY"]
DB_URL       = os.environ.get("MOVIES_DB_URL", "sqlite:///movies.db")
