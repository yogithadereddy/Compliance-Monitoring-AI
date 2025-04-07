from google.generativeai import list_models
import google.generativeai as genai

genai.configure(api_key="AIzaSyDV2bZEOXxchdyPUpYqs_kbhheiX4erzqw")

for model in list_models():
    print(model.name, " | ", model.supported_generation_methods)
