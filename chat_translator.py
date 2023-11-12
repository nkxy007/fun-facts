import openai
import os


openai.api_key = os.environ.get("OPEN_AI_KEY")

def translate(text, original_language, other_language):
    pre_prompt = """you are a language translation expert, translate text and 
    return json object like {'translation':'translated text'}je suis football m"""

    prompt = f"""translate the following {original_language} {text} into {other_language},
    """
    response = openai.ChatCompletion.create(
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



if __name__ == "__main__":
    text = input("enter text to translate:")
    original_language = input("\nwhich language:")
    translate_to = input("\ntranslate to:")
    print(translate(text,original_language, translate_to))