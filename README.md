# 📩 SMS Spam Classifier using LLM (GPT-2)

This project is an **SMS spam classifier** built on top of a fine-tuned **GPT-2-based language model**. It leverages modern tooling in Python, such as `pydantic`, `loguru`, `ruff`, and `make`, to deliver a clean, maintainable, and scalable machine learning pipeline.

## 🚀 Features

- 🧠 Fine-tuned **GPT-2** model for binary SMS classification (spam vs ham)
- 🔄 **Balanced dataset** preprocessing
- 🛡️ **Pydantic** for robust data validation
- 📊 Dataset metrics and confusion matrix visualization
- 📦 Tooling includes `ruff`, `loguru`, and `make` for linting, logging, and workflow automation

## 🧰 Tech Stack

- Python 3.12+
- Transformers (HuggingFace)
- Datasets
- Pydantic
- Loguru
- Ruff
- Make

## 📁 Project Structure

sms-classifier-llm/ ├── data/ # Raw and processed datasets ├── model/ # GPT-2 fine-tuning scripts and configs ├── notebooks/ # Experimentation notebooks ├── src/ │ ├── preprocessing.py # Data cleaning & balancing │ ├── train.py # Model training pipeline │ └── evaluate.py # Evaluation scripts ├── pyproject.toml # Project dependencies ├── Makefile # Automation commands └── README.md

## ⚙️ Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/sms-classifier-llm.git
cd sms-classifier-llm
uv venv
uv pip install -r requirements.txt
source .venv/bin/activate  # Unix
.venv\Scripts\activate     # Windows
