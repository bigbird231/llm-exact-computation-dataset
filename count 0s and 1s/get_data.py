import random
import json

random.seed(42)

def generate_sample(min_len=80, max_len=120):
    length = random.randint(min_len, max_len)
    sequence = ''.join(random.choice(['0', '1']) for _ in range(length))

    # special cases
    p = random.random()
    if p < 0.1:
        sequence = '0' * length
    elif p < 0.2:
        sequence = '1' * length

    count_0 = sequence.count('0')
    count_1 = sequence.count('1')
    answer_str = f"0:{count_0} | 1:{count_1}"

    instructions = [
        "Return the separate counts of 0s and 1s in the sequence",
        "Count how many 0s and how many 1s are in the sequence",
        "Calculate the separate number of zeros and ones",
        "Find count_0 and count_1 for the binary sequence",
        "Return how many 0s appear and how many 1s appear",
        "Can you tell me the separate counts of 0s and 1s?",
        "Give the count of zeros and the count of ones",
        "Please compute count_0 and count_1",
        "Determine the frequency of 0 and the frequency of 1",
        "Analyze the binary sequence and return separate counts for 0 and 1",
    ]

    instruction = random.choice(instructions)

    return {
        "task_type": "binary_count",
        "instruction": instruction,
        "input": sequence,
        "length": length,
        "output": {
            "count_0": count_0,
            "count_1": count_1,
            "answer": answer_str
        },
        "target_code": "seq = input_data\nprint(f\"0:{seq.count('0')} | 1:{seq.count('1')}\")"
    }


def generate_dataset(num_samples=1000, save_path="binary_dataset.jsonl"):
    with open(save_path, 'w') as f:
        for _ in range(num_samples):
            sample = generate_sample()
            f.write(json.dumps(sample) + '\n')


generate_dataset(1000)