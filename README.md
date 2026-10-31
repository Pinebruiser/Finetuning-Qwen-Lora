# Arch Linux CLI Debugging Assistant

## Overview
This repository contains the end-to-end pipeline for training and deploying a highly specialized, localized Large Language Model (LLM) designed to troubleshoot Arch Linux terminal errors. The project fine-tunes Qwen2.5-Coder (1.5B/7B) using QLoRA and serves the resulting quantized model locally via Ollama and llama.cpp. 

The primary objective is to replace generalized AI assistants with a deterministic, zero-shot terminal agent capable of providing production-ready bash solutions without conversational filler. For theoretical foundations on distributed training, model quantization, and the underlying mathematical mechanics, please refer to the file Gemini-_28.pdf.

## Architecture
The system architecture bridges advanced Parameter-Efficient Fine-Tuning (PEFT) theory with practical local deployment constraints on a CachyOS environment.
- **Base Model:** Qwen/Qwen2.5-Coder (1.5B or 7B).
- **Framework:** Unsloth for rapid, memory-optimized 4-bit fine-tuning.
- **Serving:** Merged GGUF adapter deployment natively running via Ollama/llama.cpp.

## Dataset Engineering
The dataset is programmatically sourced from the Unix & Linux Stack Exchange API, targeting questions strictly tagged with `arch-linux` and `error`. To prevent the model from learning a "forum persona" (e.g., autoregressive degeneration into hallucinated markdown rules or "Hope this helps!" sign-offs), the raw data undergoes strict sanitation:
-**Clean API RESPONSE**: To ensure that the answer for each question is the one that actually did fix the problem, Clean-QA-Dataset goes through all questions and finds the questions with accepted answer, if there is an accepted answer it gets it's id and gets the corresponding answer using said id.
- **Regex Sanitization:** Target fields (`body_markdown`) are stripped of updates, edits, and conversational signatures to leave only the technical error and the solution.
- **Schema Transformation:** The cleaned data is standardized into the multi-turn ShareGPT format (`role`/`content`), allowing native compatibility with ChatML syntax.
- **Persona Injection:** A system prompt is injected into every training record to uniformly condition the model as an expert Arch Linux systems engineer.

## Training Pipeline
The Supervised Fine-Tuning (SFT) phase relies on precision constraints to prevent catastrophic forgetting and overfitting.
- **Loss Masking:** System and user prompts are masked using `train_on_responses_only` to calculate loss exclusively on the terminal fix, this is done to ensure the model is trained to correct responses
- **Target Modules:** LoRA adapters are applied to all linear modules (Q, K, V, O, and MLP projections), this was done by following the original QLORA paper.

## Inference and Deployment
- **Local Serving:** The final LoRA weights are merged into the base model and quantized to a `q4_k_m` GGUF format. You can pull and run the model locally directly from Hugging Face using Ollama with the following command:

```bash
ollama run hf.co/Pinebruiser/arch-qwen-gguf
```