#importing dependecies make sure that the conda environment is activated

import os
import requests
import json
from typing import List
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display, update_display
from openai import OpenAI
# import ollama


# load_dotenv()
api_key = 'ollama'

if api_key:
    print("Looks good")
else:
    print("There is some prblem with the key")


# MODEL = 'gpt-4o-mini'
MODEL = "llama3.2"
openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')


class Website():
    """"
    A utility calss to represent a Website that we have scrapped, now with link
    """

    url : str
    title : str
    body : str
    links : List[str]
    text : str

    def __init__(self, url):
        self.url = url
        response = requests.get(url)
        self.body = response.content
        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        if soup.body:
            for irrelevant in soup.body(("script", "style", "img","input")):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n",strip=True)
        else:
            self.text = ""
        links = [link.get('href') for link in soup.find_all('a')]
        self.links = [link for link in links if link]
    def get_content(self):
        return f"Webpage Title:\n{self.title}\nWebpage Conntents:\n{self.text}\n\n"

# ed = Website('http://edwarddonner.com')
# print(ed.get_content())
# print(ed.links)



link_system_prompt = "You are provided with a list of links found on a webpage. \
You are able to decide which of the links would be most relevant to include in a brochure about the company, \
such as links to an About page, or a Company page, or Careers/Jobs pages.\n"
link_system_prompt += "You should respond in JSON as in this example:"
link_system_prompt += """
{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page": "url": "https://another.full.url/careers"}
    ]
}
"""


def get_links_user_prompt(website):
    user_prompt = f"Here is the list of links on the website of {website.url} - "
    user_prompt += "please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. \
Do not include Terms of Service, Privacy, email links.\n"
    user_prompt += "Links (some might be relative links):\n"
    user_prompt += "\n".join(website.links)
    return user_prompt


def get_links(url):
    website = Website(url)
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompt(website)}
      ],
        response_format={"type": "json_object"}
    )
    result = response.choices[0].message.content
    print("*"*200)
    print(json.loads(result))
    print("*"*200)
    return json.loads(result)

# print("*"*100,"\n",get_links("https://anthropic.com"))


# def get_all_details(url):
#     result = "Landing page:\n"
#     result += Website(url).get_content()
#     links = get_links(url)
#     print("Found links", links)
#     for link in links["links"]:
#         result += f"\n\n(link['type])\n"
#         result += Website(link["url"]).get_content()
#     return result


def get_all_details(url):
    result = "Landing page:\n"
    result += Website(url).get_content()
    links = get_links(url)
    print("Found links:", links)
    for link in links["links"]:
        result += f"\n\n{link['type']}\n"
        result += Website(link["url"]).get_content()
    return result
# print(get_all_details("https://anthropic.com"))


system_prompt = "You are an assistant that analyzes the contents of several relevant pages from a company website \
and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown.\
Include details of company culture, customers and careers/jobs if you have the information."


def get_brochure_user_prompt(company_name, url):
    user_prompt = f"You are looking at a company called: {company_name}\n"
    user_prompt += f"Here are the contents of its landing page and other relevant pages; use this information to build a short brochure of the company in markdown.\n"
    user_prompt += get_all_details(url)
    user_prompt = user_prompt # Truncate if more than 5,000 characters
    return user_prompt

def create_brochure(company_name, url):
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
          ],
    )
    result = response.choices[0].message.content
    display(Markdown(result))
    # print(Markdown(result))
    

create_brochure("Anthropic", "https://anthropic.com")