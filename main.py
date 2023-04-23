from models.search import SearchEngine
from models.add_context import handle_stream, generate_prompt, post_answer
import os
from dotenv import load_dotenv

load_dotenv()
key = 'API_KEY'
api_key = os.getenv(key)

s_e = SearchEngine(10)
search_term = 'Did the hornets win last night?'
sources = s_e.search(search_term)
prompt = generate_prompt(sources)
data = post_answer(prompt, api_key)
