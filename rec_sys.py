import google.generativeai as genai
from json import loads

genai.configure(api_key='') #enter gemini api key

# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "application/json",
}
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_ONLY_HIGH",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
]

def get_result(listA,listB):
  try:
    model = genai.GenerativeModel(
      model_name="gemini-1.5-flash-latest",
      safety_settings=safety_settings,
      generation_config=generation_config,
      system_instruction="i will give you a list 'A'  and list 'B' of movies for each prompt and you have to give a list of 10 movies that you recommend me based on those movies in list 'A' , they should be similar to them, make sure there are no duplicates and none of the movies are from the list 'B' or 'A'  as i have already watched all the movies from those lists. reply with just the list of movies in a json format containing the list of the 10 movies, the names should be very specific to avoid confusion between movies with the same name",
    )

    chat_session = model.start_chat(
      history=[
      ]
    )

    print(f"lista:{listA} , listB:{listB}")

    response = chat_session.send_message(f"list A : {listA}, list B: {listB}")

    print(model.count_tokens(chat_session.history))

    return response.text
  except Exception as e:
     print(e)
     return None
  
if __name__ == "__main__":
    while True:
        a = input("List A : ")
        b = input("List B : ")
        recomendations = get_result(a,b)
        print(recomendations)
        recomendations = loads(recomendations)

        for i in recomendations:
            print(i)