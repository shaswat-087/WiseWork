import json
import requests
from flask import Flask,render_template,request,redirect,url_for,session
import os
from groq import Groq
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

x_key=os.getenv("X_API_KEY")
app=Flask(__name__)
app.secret_key='your_key'
@app.route("/")
def index():
    return render_template('index.html')


class City_Analysis(BaseModel):
    intro:list[str]=Field(description="An indroductory text about the workplace city and how it feels to work there." \
    "STRICT CONSTRAINT: Do NOT include generic stuff like 'rich cultural heritage' , and MUST include the importance of the city and special names if any. ")
    city:str=Field(description="Name of the city")
    it:list[str]=Field(description="3 to 4 updated,grounded insights regarding local tech salaries, top companies hiring trends of the city and major it hubs and importance of the city in country's IT sector field and AI/ML")
    core:list[str]=Field(description="3 to 4 distinct key facts and modern insights in candid tone, regarding core industries in the area, salaries,  hiring trends of the city and importance of the city in country's core industry and special names if any." \
    "STRICT CONSTRAINT: Do NOT claim facts without grounding,unless specifying R&D or automotive companies specifically.Do NOT include companies that shut down its operations earlier.")
    climate:list[str]=Field(description="1 to 3 sentences about climate of the city and extreme seasonal hazards, like- excessive south-west or north-east monsoon, strictly only one among these two kind of monsoon,waterlogging, water scarcity, humidity or scorching heat- any one or two among these,whichever applies in that case")
    wlb:list[str]=Field(description="Average work hours,management style and work life balance in the city-3 to 5 point in warm but realistic tone .Also include living costs and salary vs cost analysis .Living cost should include house rent and food costs in different areas of the city")

    culture:list[str]=Field(description="Brief description of culture and tourist attractions of the city.Also mention the food cuisine of the city and how it is adjustable to outsiders.Must mention the cultural/language constraints a new-comer or outsider may face in the city.Also mention the advantages or hospitality for newcomers " \
    "STRICT CONSTRAINT: Do not repeat words from intro.")
    govt:list[str]=Field(description="Brief description of the initiatives taken by current govt (as of 2026) for industrial growth, transportation and infrastructure in the region." \
    "STRICT CONSTRAINT: MUST include recent facts in the time period 2023-26. Use only current 2026 level government actions.No outdated facts before 2023-26.")
    fresher:list[str]=Field(description="Brief guidance about should a fresher choose the city as workplace in current situation and what fits their preferences ")
class City_Compare(BaseModel):
    city_1_name: str = Field(description="Name of the first city being analyzed")
    city_2_name: str = Field(description="Name of the second city being analyzed")
    it:list[str]=Field(description="3 distinct key comparisons regarding local tech salaries, top companies hiring trends of  the cities and major it hubs and importance of the cities in Indian IT sector field and AI/ML.")
    core:list[str]=Field(description="3 to 4 distinct key facts comparing core industries in the area, salaries,  hiring trends of the cities and comparative importance of the cities in Indian core industry and special names if any." \
    "STRICT CONSTRAINT: MUST provide the facts related to city1 and city2.")
    climate:list[str]=Field(description="1 to 3 key information about climate of the city and extreme seasonal hazards, like- excessive monsoon,waterlogging, water scarcity, humidity or scorching heat- any one or two among these,whichever applies in that case")
    wlb:list[str]=Field(description="Average work hours,management style and work life balance in the city-3 points." \
    "STRICT CONSTRAINT: MUST provide the facts related to city1 and city2 separately. MUST include salary vs living cost factor. Living cost should include house rent and food costs in different areas of those two cities")
    culture:list[str]=Field(description="Brief description of culture and tourist attractions of the city.Must mention the cultural/language constraints a new-comer or outsider may face in the city.Also mention the advantages or hospitality for newcomers " \
        "STRICT CONSTRAINT: Do NOT repeat words from intro.")
    guidance:list[str]=Field(description="Give an actioanable advice based on the comparative analysis of both the cities and which kind of job/roles preference fit which workplace better. And also take note of cultural preferences")


def system_prompt(selected_schema):
                    return( "You are a sharp, realistic local industry insider and career advisor. "
                            "Your tone should be candid, grounded, and practical—avoid generic fluff but use natural,helpful language with sharp,updated information as of 2026. "
                            "Mention or cite policies or initiatives only in the time period of 2023-26.\n\n"
                            "Mention specifically local startups/companies of that city only which gained significant traction. Do NOT mention startups from other cities"
                            "- Do NOT mention Ford, General Motors, or defunct automakers as active mass recruiters in India.\n"
        
                            "In core and IT field separately mention fresher level and mid/senior level salaries/hiring trends\n\n"
                             "Provide specific, practical details and real life challenges challenges that a professional moving there tomorrow needs to know.\n\n" "You MUST respond with a valid JSON object strictly matching this schema:\n"
                    f"{json.dumps(selected_schema.model_json_schema())}\n\n"
                    "Do NOT wrap the response in a parent key like 'workplace_culture', 'data', or 'analysis'. The root JSON object must directly contain the schema fields.\n"
                    "Do not include markdown code block formatting (like ```json), greetings, or extra conversational text."
                    "Do not include repeated facts,or adjectives in multiple keys. Every field must carry distinct, non-overlapping insights. No duplicates."
                    "Do not use meta-narratives like 'reddit threads mention this' or 'here is your analysis'."
                    "Use language that can be helpful to a newcomer in the city."
                    "Do not use fluff language like 'rich cultural heritage', 'mix of modern and traditional','burstling metropolis'"
                    )
def search(query: str) -> str:
    #Fetches real-time search context using Serper API.
    url="https://google.serper.dev/search"
    payload=json.dumps({"q": query, "num": 6})
    headers={
        'X-API-KEY':x_key,
        'Content-Type': 'application/json'
    }
    try:
        response=requests.post(url, headers=headers, data=payload)
        res_data=response.json()
        
        
        snippets=[]
        for item in res_data.get("organic", []):
            title=item.get("title", "")
            snippet=item.get("snippet", "")
            snippets.append(f"Source: {title}\nInfo: {snippet}")
            
        return "\n\n".join(snippets)
    except Exception as e:
        print(f"Warning: Serper search grounding failed: {e}")
        return "No external grounding retrieved."

from functools import lru_cache



           
def fetch_client(selected_schema,system_prompt,user_prompt):    
 client = Groq(api_key=os.getenv("GROQ_API_KEY"))
 response=client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "system",
            "content": system_prompt(selected_schema),
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ],
    response_format={"type": "json_object"},
    temperature=0.5,
    max_tokens=3000,
   )

 if selected_schema==City_Analysis:
       
       data: City_Analysis= City_Analysis.model_validate_json(
        response.choices[0].message.content)
       message={
                "city": data.city,
                "intro": data.intro,
                 "it": data.it,
                 "core": data.core,
                 "wlb": data.wlb,
                 "climate": data.climate,
                 "culture": data.culture,
                 "govt": data.govt,
                 "fresher":data.fresher
                             }
       return message
 
 else:
    comp_data: City_Compare = City_Compare.model_validate_json(response.choices[0].message.content)
    comparison= {
        "city_1": comp_data.city_1_name,
        "city_2": comp_data.city_2_name,
        "it": comp_data.it,
        "core": comp_data.core,
        "climate": comp_data.climate,
        "wlb": comp_data.wlb,
        "culture": comp_data.culture,
        "guidance": comp_data.guidance,
    }
    return comparison

@lru_cache(maxsize=100)
def cached_city(city_name: str):
    city=city_name.strip().title()
    grounding=search(f"{city} tech salaries core industries infrastructure govt developments reddit workplace culture 2025 2026")
    user_prompt=f"Analyze workplace culture in {city}.\n\n### SEARCH GROUNDING CONTEXT:\n{grounding}"
    return fetch_client(City_Analysis,system_prompt, user_prompt)


@lru_cache(maxsize=100)
def cached_comparison(city1: str, city2: str):
    c1,c2=city1.strip().title(), city2.strip().title()
    g1=search(f"{c1} tech salaries core industries workplace culture climate govt initiatives 2025 2026")
    g2=search(f"{c2} tech salaries core industries workplace culture climate govt initiatives 2025 2026")
    user_prompt=f"Compare workplace culture in {c1} vs {c2}.\n\n### SEARCH GROUNDING CONTEXT FOR {c1}:\n{g1}\n\n### SEARCH GROUNDING CONTEXT FOR {c2}:\n{g2}"
    return fetch_client(City_Compare, system_prompt,user_prompt)

@app.route("/city",methods=['GET','POST'])
def city():
      if request.method=='GET':
            message = session.pop('message', None)
            return render_template('city.html')
      if request.method=='POST':
                  city=request.form.get('Cityname')
                  selected_schema=City_Analysis
                  grounding_data=search(f"{city} tech salaries core industries infrastructure govt developments reddit workplace culture 2025 2026")
                
                  user_prompt=f"Analyze workplace culture in {city}.\n\n### SEARCH GROUNDING CONTEXT:\n{grounding_data}"
                  message=cached_city(city)
                  
                  
                  return render_template('city.html',message=message)
      return redirect(url_for('city'))

@app.route('/compare',methods=['GET','POST'])
def compare():
    if request.method=='GET':
             message = session.pop('message', None)
             return render_template('compare.html')
    if request.method=='POST':
             city1=request.form.get('city1')
             city2=request.form.get('city2')
             selected_schema=City_Compare
             grounding_data_1 = search(f"{city1} tech salaries core industries workplace culture climate govt initiatives 2025 2026")
             grounding_data_2 = search(f"{city2} tech salaries core industries workplace culture climate govt initiatives 2025 2026")
          
             user_prompt = f"Compare workplace culture in {city1} vs {city2}.\n\n### SEARCH GROUNDING CONTEXT FOR {city1}:\n{grounding_data_1}\n\n### SEARCH GROUNDING CONTEXT FOR {city2}:\n{grounding_data_2}"
             message=cached_comparison(city1,city2)
                               
             return render_template('compare.html',message=message)
    return redirect(url_for('compare'))
   

if __name__ == "__main__":
      app.run(debug=True)
      
