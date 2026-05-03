from openai import OpenAI

openai_api_key = "sk-834def25569545e6b2c71137b7676d9b"
openai_api_base = "https://llm-api.arc.vt.edu/api/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

model = "gpt-oss-120b"

def human_prompt_parser():
    input_data = '01101111100010001001111111000011001110001000111011110000001111100000011111011111000001010011'
    print(len(input_data), input_data.count('0'), input_data.count('1'))

    # read prompt template
    with open("prompt2.txt", "r") as f:
        prompt_template = f.read()

    prompt = prompt_template.replace("{input_data}", input_data)

    messages = [
        {"role": "system", "content": "Do the task."},
        {"role": "user", "content": prompt},
    ]
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )

        result = response.choices[0].message.content.strip().lower()

        print(36, "Result:", result)

        return result
    except:
        return "something went wrong"


# result = human_prompt_parser()
