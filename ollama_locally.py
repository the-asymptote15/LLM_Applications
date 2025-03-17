import requests
from bs4 import BeautifulSoup
from IPython.display import Markdown,display
import ollama



OLLAMA_API = "http://localhost:11434/api/chat"
HEADER = {"COntent-Type":"application/json"}
MODEL = "llama3.2"

message = [{"role": "user", "content":"Describe some of the bussiness application of Generative AI"}]

response = ollama.chat(model = MODEL, messages = message)
print(response['message']['content'])