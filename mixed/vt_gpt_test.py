from openai import OpenAI
import json
import random
import re
import time
from collections import Counter


SAMPLE_NUMBER = 90
# PROMPT_FILE = "prompt1_plain_mixed.txt"
# PROMPT_FILE = "prompt2_CoT_mixed.txt"
# PROMPT_FILE = "prompt3_least_to_most_mixed.txt"
# PROMPT_FILE = "prompt4_PoT_mixed.txt"
PROMPT_FILE = "prompt5_self_consistency_mixed.txt"

DATASET_PATHS = {
    "binary_count": "binary_dataset.jsonl",
    "longest_substring": "substring_dataset.jsonl",
    "arithmetic": "arithmetic_dataset.jsonl",
}

random.seed(42)

openai_api_key = "sk-834def25569545e6b2c71137b7676d9b"
openai_api_base = "https://llm-api.arc.vt.edu/api/v1"
client = OpenAI(api_key=openai_api_key, base_url=openai_api_base)
model = "gpt-oss-120b"


def build_prompt(prompt_template, sample):
    return (
        prompt_template
        .replace("{task_type}", sample["task_type"])
        .replace("{instruction}", sample["instruction"])
        .replace("{input_data}", sample["input"])
        .replace("{target_char}", sample.get("target_char", ""))
    )


def parse_binary(result):
    match = re.search(r"0\s*:\s*(\d+)\s*\|\s*1\s*:\s*(\d+)", result)
    if match:
        return f"0:{int(match.group(1))} | 1:{int(match.group(2))}"
    return None


def parse_integer(result):
    nums = re.findall(r"-?\d+", result)
    if nums:
        return str(int(nums[-1]))
    return None


def parse_by_task(result, task_type):
    if isinstance(result, tuple):
        return result

    if task_type == "binary_count":
        return parse_binary(result)
    elif task_type in ["longest_substring", "arithmetic"]:
        return parse_integer(result)
    return None


def clean_code(code):
    code = code.strip()
    code = re.sub(r"```python", "", code, flags=re.IGNORECASE)
    code = re.sub(r"```", "", code)
    return code.strip()


def execute_code(code_str, sample):
    local_vars = {
        "input_data": sample["input"],
        "target_char": sample.get("target_char", ""),
    }

    try:
        import io
        import contextlib

        code_str = clean_code(code_str)

        blocked_patterns = ["input(", "sys.stdin", "open(", "while true"]
        if any(p in code_str.lower() for p in blocked_patterns):
            print("Execution blocked: unsafe or hanging code")
            return ""

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            exec(code_str, {}, local_vars)

        return f.getvalue().strip().lower()

    except Exception as e:
        print("Execution error:", e)
        return ""


def request_gpt(sample, prompt_template):
    prompt = build_prompt(prompt_template, sample)

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


def request_gpt_sc(sample, prompt_template, n=5):
    results = []
    sc_record = ""

    for j in range(n):
        try:
            prompt = build_prompt(prompt_template, sample)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Do the task."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )

            raw = response.choices[0].message.content.strip().lower()
            print("Single SC:", raw)
            sc_record += f"Single SC {j + 1}: {raw}\n"

            parsed = parse_by_task(raw, sample["task_type"])
            if parsed is not None:
                results.append(parsed)

        except Exception as e:
            print("SC API error:", e)
            sc_record += f"Single SC {j + 1}: API error: {e}\n"

        time.sleep(1)

    if not results:
        return None, sc_record

    counter = Counter(results)
    return counter.most_common(1)[0][0], sc_record


def load_mixed_dataset(samples_per_task=40):
    mixed_data = []

    for task_type, path in DATASET_PATHS.items():
        with open(path, "r", encoding="utf-8") as f:
            dataset = [json.loads(line) for line in f]

        sampled = random.sample(dataset, samples_per_task)
        mixed_data.extend(sampled)

    random.shuffle(mixed_data)
    return mixed_data


def test_dataset(sample_number=120):
    samples_per_task = sample_number // 3

    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    sampled_data = load_mixed_dataset(samples_per_task)

    correct = 0
    record = ""

    task_stats = {
        "binary_count": {"correct": 0, "total": 0},
        "longest_substring": {"correct": 0, "total": 0},
        "arithmetic": {"correct": 0, "total": 0},
    }

    print("Sampled data:", len(sampled_data))

    for i, sample in enumerate(sampled_data):
        task_type = sample["task_type"]
        gold_answer = sample["output"]["answer"]

        task_stats[task_type]["total"] += 1

        currentRecord = ""
        currentRecord += f"\nSample {i + 1}/{len(sampled_data)}\n"
        currentRecord += f"Task type: {task_type}\n"
        currentRecord += f"Instruction: {sample['instruction']}\n"
        currentRecord += f"Input: {sample['input']}\n"
        currentRecord += f"Ground truth: {gold_answer}\n"
        currentRecord += "---------\n"

        if PROMPT_FILE == "prompt5_self_consistency_mixed.txt":
            result, sc_record = request_gpt_sc(sample, prompt_template)
            currentRecord += sc_record
            pred_answer = result
            currentRecord += f"GPT voted result: {pred_answer}\n"

        elif PROMPT_FILE == "prompt4_PoT_mixed.txt":
            code_result = request_gpt(sample, prompt_template)
            currentRecord += f"GPT raw code:\n{code_result}\n"

            exec_result = execute_code(code_result, sample)
            currentRecord += f"Execution result: {exec_result}\n"

            pred_answer = parse_by_task(exec_result, task_type)

        else:
            result = request_gpt(sample, prompt_template)
            currentRecord += f"GPT raw result: {result}\n"

            pred_answer = parse_by_task(result, task_type)

        is_correct = pred_answer == gold_answer

        if is_correct:
            correct += 1
            task_stats[task_type]["correct"] += 1
            currentRecord += f"Predicted: {pred_answer}\n"
            currentRecord += "Correct\n"
        else:
            currentRecord += f"Predicted: {pred_answer}\n"
            currentRecord += "Wrong\n"

        currentRecord += "\n"
        print("=" * 50)
        print(currentRecord)

        record += currentRecord

        with open(f"{PROMPT_FILE}_record.txt", "a", encoding="utf-8") as f:
            f.write(currentRecord)

        time.sleep(1)

    mixed_accuracy = correct / len(sampled_data)

    final_record = "\n========== Per-task Result ==========\n"
    for task_type, stat in task_stats.items():
        acc = stat["correct"] / stat["total"]
        final_record += f"{task_type}: {stat['correct']}/{stat['total']} = {acc:.4f}\n"

    final_record += "\n========== Final Mixed Result ==========\n"
    final_record += f"Final mixed accuracy: {mixed_accuracy:.4f}\n"
    final_record += f"Correct: {correct}/{len(sampled_data)}\n"

    print(final_record)

    with open(f"{PROMPT_FILE}_record.txt", "a", encoding="utf-8") as f:
        f.write(final_record)


test_dataset(sample_number=SAMPLE_NUMBER)