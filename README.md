# 📊 LLM Exact Computation Dataset

This repository provides a synthetic dataset and evaluation framework for studying **deterministic computation in Large Language Models (LLMs)**.

We focus on tasks where **exact correctness is required**, including:
- Binary counting (0s and 1s)
- Longest substring computation
- Arithmetic expression evaluation

---

## 📌 Motivation

LLMs are powerful for language understanding, but they often struggle with **exact computation tasks**, where:
- No approximation is allowed
- Small errors lead to completely incorrect outputs

This project evaluates:
- Prompting strategies (Plain, CoT, Least-to-Most, PoT, Self-Consistency)
- Program-based reasoning (PoT)
- Small task-specific models (CodeT5)

---

## 📁 Repository Structure

### 1. `dataset/`
Core dataset (1000 samples per task):

dataset/
├── binary_dataset.jsonl
├── substring_dataset.jsonl
├── arithmetic_dataset.jsonl

Each file contains:
- Natural language instruction (diverse)
- Input data
- Ground truth output
- Reference Python solution (`target_code`)

---

### 2. `count 0s and 1s/`
Single-task evaluation (binary counting only):

count 0s and 1s/
├── prompt1_plain.txt
├── prompt2_cot.txt
├── prompt3_least_to_most.txt
├── prompt4_pot.txt
├── prompt5_sc.txt
├── record_prompt1.txt
├── record_prompt2.txt
...

Includes:
- Prompt templates
- Full evaluation logs for each method

---

### 3. `mixed/`
Mixed-task evaluation (generalization setting):

mixed/
├── prompt1_plain.txt
├── prompt2_cot.txt
├── prompt3_least_to_most.txt
├── prompt4_pot.txt
├── prompt5_sc.txt
├── record_prompt1.txt
├── record_prompt2.txt
...

Includes:
- Multi-task evaluation logs
- All prompting strategies

---

## 🧩 Dataset Format

Each sample follows this structure:

```json
{
  "task_type": "binary_count",
  "instruction": "Determine the frequency of 0 and the frequency of 1",
  "input": "0010000010...",
  "length": 120,
  "output": {
    "count_0": 65,
    "count_1": 55,
    "answer": "0:65 | 1:55"
  },
  "target_code": "seq = input_data\nprint(f\"0:{seq.count('0')} | 1:{seq.count('1')}\")"
}
```

### Design Highlights

- Generalized instructions (multiple phrasings)
- Executable ground truth via Python code
- Standardized answer format

---

## 🧪 Tasks Overview

### Binary Counting
Count number of 0s and 1s in a sequence (length 80–120)

### Longest Substring
Find longest consecutive occurrence of a target character

### Arithmetic Computation
Evaluate expressions with integer outputs

---

## ⚙️ Evaluation Methods

We evaluate 5 approaches:

| Method | Description |
|------|------------|
| Plain | Direct answer |
| CoT | Step-by-step reasoning |
| Least-to-Most | Decomposition |
| PoT | Generate + execute code |
| SC | Majority voting (5 samples) |

---

## 📊 Key Findings

- LLMs struggle with exact computation
- CoT provides limited benefit
- Least-to-Most accumulates errors
- PoT achieves near-perfect accuracy
- Self-Consistency improves accuracy but is costly
- CodeT5-small achieves perfect accuracy with minimal training

---

## 🚀 Usage

### Load dataset

```python
import json

with open("binary_dataset.jsonl") as f:
    data = [json.loads(line) for line in f]
```

---

## 📎 Citation

```bibtex
@misc{llm_exact_computation,
  title={Evaluating Prompting Strategies for Deterministic Computation in LLMs},
  author={Hongkun Yu},
  year={2026}
}
```

---

## 💡 Notes

This dataset is designed to:
- Stress-test exact reasoning
- Separate language ability from computation ability
- Encourage tool-augmented LLM research
