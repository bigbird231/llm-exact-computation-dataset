# 📊 LLM Exact Computation Dataset

A lightweight benchmark for evaluating **deterministic computation in Large Language Models (LLMs)**.

---

## 📌 Overview

This project studies how well LLMs perform on tasks requiring **exact correctness**:

- Binary counting (0s and 1s)  
- Longest substring computation  
- Arithmetic evaluation  

We compare prompting methods and a small code model under a **controlled synthetic dataset**.

---

## 📁 Structure

- **dataset/** → core data (1000 samples per task)  
- **count 0s and 1s/** → single-task evaluation  
- **mixed/** → multi-task evaluation 

---

## 🧩 Data Format

```json
{
  "task_type": "binary_count",
  "instruction": "...",
  "input": "...",
  "output": {
    "answer": "0:65 | 1:55"
  },
  "target_code": "..."
}
```

✔ Diverse instructions  
✔ Exact answers  
✔ Executable ground truth  

---

## ⚙️ Methods

- Plain Prompt  
- CoT (Chain-of-Thought)  
- Least-to-Most  
- PoT (Program-of-Thought)  
- Self-Consistency  
- CodeT5-small (fine-tuned)  

---

## 📊 Results

### Mixed Task Accuracy

| Method | Accuracy |
|------|--------|
| Plain | 0.68 |
| CoT | 0.65 |
| Least-to-Most | 0.62 |
| PoT | **1.00** |
| Self-Consistency | 0.72 |
| CodeT5-small | **1.00** |

---

## 🔑 Key Findings

- LLMs struggle with exact symbolic computation  
- CoT provides limited improvement  
- Least-to-Most suffers from error accumulation  
- PoT achieves perfect accuracy via code execution  
- Self-Consistency improves accuracy but is costly  
- CodeT5-small achieves perfect accuracy with minimal training  

---

## 🚀 Quick Start

```python
import json

with open("dataset/binary_dataset.jsonl") as f:
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

## 💡 Summary

This benchmark highlights a key gap:

LLMs are strong at language — but not reliable for exact computation  
unless combined with tools (PoT) or task-specific models
