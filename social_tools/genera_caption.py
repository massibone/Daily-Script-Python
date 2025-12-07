'''
Usa LLM per creare caption engaging da una descrizione scatto, con emoji e CTA per massimizzare interazioni su foto X100V 
'''

import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
