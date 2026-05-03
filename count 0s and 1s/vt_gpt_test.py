from openai import OpenAI
import json
import random
import re
import time
from collections import Counter


# Global Settings
SAMPLE_NUMBER = 2
PROMPT_FILE = "prompt1_plain.txt"
DATASET_PATH = "binary_dataset.jsonl"
random.seed(42)

# VT_GPT Api Key
openai_api_key = "sk-834def25569545e6b2c71137b7676d9b"
openai_api_base = "https://llm-api.arc.vt.edu/api/v1"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)
model = "gpt-oss-120b"


def parse_result(result):
    match = re.search(r"0:(\d+)\s*\|\s*1:(\d+)", result)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

# prompt3_least_to_most
def parse_result_chunk(result):
    final_match = re.search(
        r"final\s*:\s*(?:\n|\r|\s)*0\s*:\s*(\d+)\s*\|\s*1\s*:\s*(\d+)",
        result,
        re.IGNORECASE
    )
    if final_match:
        return int(final_match.group(1)), int(final_match.group(2))

    matches = re.findall(
        r"0\s*:\s*(\d+)\s*\|\s*1\s*:\s*(\d+)",
        result,
        re.IGNORECASE
    )
    if matches:
        last_match = matches[-1]
        return int(last_match[0]), int(last_match[1])

    return None, None

# prompt4_PoT
def execute_code(code_str, input_data):
    local_vars = {}
    try:
        # inject seq variable
        exec("seq = '''{}'''".format(input_data), {}, local_vars)

        # capture print output
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            exec(code_str, {}, local_vars)

        output = f.getvalue().strip().lower()
        return output

    except Exception as e:
        print("Execution error:", e)
        return ""

# prompt5_self_consistency
def request_gpt_sc(input_data, prompt_template, n=5):
    results = []
    raw_outputs = []
    sc_record = ''

    for j in range(n):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Do the task."},
                    {"role": "user", "content": prompt_template.replace("{input_data}", input_data)},
                ],
                temperature=0.7,
            )

            raw = response.choices[0].message.content.strip().lower()
            print("Single SC:", raw)
            sc_record += f"Single SC {j + 1}: {raw}\n"

            raw_outputs.append(raw)

            parsed = parse_result(raw)
            if parsed != (None, None):
                results.append(parsed)

        except Exception as e:
            print("SC API error:", e)
            sc_record += f"Single SC {j + 1}: API error: {e}\n"

        time.sleep(1)

    if not results:
        return (None, None), sc_record

    counter = Counter(results)
    return counter.most_common(1)[0][0], sc_record

def request_gpt(input_data, prompt_template):
    prompt = prompt_template.replace("{input_data}", input_data)

    # print(58, prompt)

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
        print("GPT Result:", result)
        return result
    except Exception as e:
        print("API error:", e)
        return "something went wrong"


def test_dataset(sample_number=100):
    with open(DATASET_PATH, "r") as f:
        dataset = [json.loads(line) for line in f]

    with open(PROMPT_FILE, "r") as f:
        prompt_template = f.read()

    sampled_data = random.sample(dataset, sample_number)

    correct = 0
    record = ""

    print("Sampled data:", len(sampled_data))
    print("\n")
    for i, sample in enumerate(sampled_data):
        input_data = sample["input"]
        gt_0 = sample["output"]["count_0"]
        gt_1 = sample["output"]["count_1"]

        currentRecord = ""
        currentRecord += f"\nSample {i + 1}/{sample_number}\n"
        currentRecord += f"Input: {input_data}\n"
        currentRecord += f"Ground truth: 0s={gt_0}, 1s={gt_1}\n"
        currentRecord += "---------\n"

        if PROMPT_FILE == 'prompt5_self_consistency.txt':
            result = request_gpt_sc(input_data, prompt_template)
            currentRecord += result[1]
            result = result[0]
            currentRecord += f"GPT voted result: {result}\n"
        elif PROMPT_FILE == 'prompt4_PoT.txt':
            code_result = request_gpt(input_data, prompt_template)
            currentRecord += f"GPT raw result:\n{code_result}\n"

            result = execute_code(code_result, input_data)
            currentRecord += f"Execution result: {result}\n"
        else:
            result = request_gpt(input_data, prompt_template)
            currentRecord += f"GPT raw result: {result}\n"

        if PROMPT_FILE == 'prompt5_self_consistency.txt':
            pred_0, pred_1 = result
        elif PROMPT_FILE == 'prompt3_least_to_most.txt':
            pred_0, pred_1 = parse_result_chunk(result)
        else:
            pred_0, pred_1 = parse_result(result)

        if pred_0 == gt_0 and pred_1 == gt_1:
            correct += 1
            currentRecord += f"Predicted: 0s={pred_0}, 1s={pred_1}\n"
            currentRecord += "Correct\n"
            # print(f"Correct, GT: {gt_0}, {gt_1}, GPT: {pred_0}, {pred_1}")
        else:
            currentRecord += f"Predicted: 0s={pred_0}, 1s={pred_1}\n"
            currentRecord += "Wrong\n"
            # print(f"Wrong, GT: {gt_0}, {gt_1}, GPT: {pred_0}, {pred_1}")

        currentRecord += "\n"
        print("=" * 50)
        print(currentRecord)
        record += currentRecord
        time.sleep(1)

    accuracy = correct / sample_number

    record += "\n========== Final Result ==========\n"
    record += f"Final accuracy: {accuracy}\n"
    record += f"Correct: {correct}/{sample_number}\n"
    print(f"Final accuracy: {accuracy}\n")

    # write to file
    with open(f"{PROMPT_FILE}_record.txt", "w", encoding="utf-8") as f:
        f.write(record)


test_dataset(sample_number=SAMPLE_NUMBER)
