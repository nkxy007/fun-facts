import openai
import os


_key = os.environ.get("OPEN_AI_KEY")
client = openai.OpenAI(
        api_key = _key
    )

def translate(text, original_language, other_language):
    pre_prompt = """you are a language translation expert, translate text and 
    return json object like {'translation':'translated text'}"""

    prompt = f"""translate the following {original_language} {text} into {other_language},
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content":pre_prompt},
            {"role":"user","content":prompt}
        ],
        max_tokens=400,
        n=1,
        stop=None,
        temperature=1,
    )
    instructions = response.choices[0].message.content.strip()
    return instructions
