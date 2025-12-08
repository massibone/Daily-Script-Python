'''
Usa LLM per creare caption engaging da una descrizione scatto, con emoji e CTA per massimizzare interazioni su foto X100V.
Descrive lo scatto, genera caption coerente per poterlo copiare direttamente su IG.
'''

import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def genera_caption(descrizione, stile="street"):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Scrivi caption Instagram per fotografia street: 1-2 frasi engaging, 1 emoji, 1 domanda CTA. Max 150 caratteri."},
            {"role": "user", "content": f"Descrizione scatto: {descrizione}. Stile: {stile}."}
        ],
        max_tokens=100
    )
    return response.choices[0].message.content.strip()
  

# Esempio
caption = genera_caption("Vicoli Firenze pioggia, riflessi luci, passanti ombre")
print(caption)
# Output: "Pioggia sui vicoli di Firenze, magia negli riflessi 🌧️ Qual è il tuo scatto sotto la pioggia preferito?"
