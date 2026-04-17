# LucaVirusCress: A Deep Learning Framework for CRESS Virus Identification

[![Model](https://img.shields.io/badge/HuggingFace-LucaVirusCress-yellow)](https://huggingface.co/Daxiao123/LucaVirusCress)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

LucaVirusCress is a specialized binary classification model for identifying CRESS (Circular Rep-Encoding Single-Stranded) DNA viruses by targeting REP (Replication-associated protein). Built on [LucaProt](https://github.com/alibaba/LucaProt), it supports high-throughput viral sequence screening in large metagenomic datasets.

## Contents

- [Project Overview](#project-overview)
- [Training Performance](#training-performance)
- [Dataset Details](#dataset-details)
- [Technical Specifications](#technical-specifications)
- [Usage](#usage)
- [Model Weights](#model-weights)
- [License](#license)

## Project Overview

- Task: Binary classification (CRESS REP vs. non-CRESS REP)
- Target: CRESS virus REP proteins
- Architecture: SequenceAndStructureFusionNetwork (SEFN), a 4-layer Transformer-based fusion network
- Application: Discovery of novel CRESS viruses from environmental and clinical omics data

## Training Performance

The model reached optimal convergence at 4,000 global steps.

The training process used weighted loss to handle extreme class imbalance.

| Metric | Set | Visualization |
| :--- | :--- | :--- |
| Confusion Matrix | Test | ![Test confusion matrix](./photo/test_confusion_matrix.png) |
| Confusion Matrix | Dev | ![Dev confusion matrix](./photo/dev_confusion_matrix.png) |
| F1 Score | Evaluation | ![F1 score](./photo/eval_f1.png) |
| Training Loss | Steps | ![Training loss](./photo/loss.png) |

## Dataset Details

To ensure high specificity, the model was trained on a highly imbalanced dataset (1:40 ratio) with carefully selected hard negatives.

- Positive samples: Verified CRESS REP protein sequences
- Negative samples:
  1. Non-CRESS proteins with high sequence similarity to REP
  2. Proteins with structural motifs similar to the target class
  3. Non-target proteins in the CRESS viral genome (for example, Cap proteins)

## Technical Specifications

| Resource | Specification |
| :--- | :--- |
| Hardware | NVIDIA L40S (46 GB VRAM) |
| Compute | 16 vCPUs |
| Software | CUDA 12.8 / Driver 570.172.08 |
| Training Time | Approximately 20 hours |

## Usage

### 1. Environment Setup

```bash
git clone https://github.com/lpyhhh/LucaVirusCress.git
cd LucaVirusCress

conda env create -f environment.yaml
conda activate lucaviruscress

# Download model files from Hugging Face
git clone https://huggingface.co/Daxiao123/LucaVirusCress hf_model

# Copy model files into checkpoint directory
mkdir -p models/cress/protein/binary_class/sefn/20230201140320/checkpoint-4000
cp -r hf_model/* models/cress/protein/binary_class/sefn/20230201140320/checkpoint-4000/

# Clean temporary directory
rm -rf hf_model
```

### 2. Single Sequence Prediction

The embedding matrix is generated in real time.

```bash
cd src

python predict_one_sample.py \
  --protein_id protein_1 \
  --sequence "MTTSTAFT...(your sequence)" \
  --emb_dir ../emb \
  --dataset_name cress \
  --dataset_type protein \
  --task_type binary_class \
  --model_type sefn \
  --time_str 20260321140320 \
  --step 4000 \
  --threshold 0.5 \
  --gpu_id 0
```

### 3. Batch Prediction (FASTA)

For large-scale screening of metagenomic assemblies:

```bash
cd src

python predict_many_samples.py \
  --fasta_file ../data/input.fasta \
  --save_file ../result/prediction_results.csv \
  --emb_dir ../emb \
  --dataset_name cress \
  --model_type sefn \
  --time_str 20260321140320 \
  --step 4000 \
  --gpu_id 0
```

### Key Parameters

- --truncation_seq_length: Maximum sequence length (default: 4096)
- --pos_weight: Handled internally (configured as 40 in config.json for imbalance)
- --threshold: Classification threshold (default: 0.5)

## Model Weights

Pre-trained weights and configuration are hosted on Hugging Face:

<https://huggingface.co/Daxiao123/LucaVirusCress>

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

## Acknowledgment

Thanks to everyone who supported this project.