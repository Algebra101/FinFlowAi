# FinCore AI

## Intelligent Financial Operating System for Nigerian SMEs

FinCore AI is a unified AI-powered financial platform designed to solve four critical challenges in Nigeria’s financial ecosystem:

- Fragmented banking data
- Poor cash flow visibility
- Limited access to credit
- Rising fraud threats

Built for the GTCo Squad Hackathon 3.0, the platform leverages Squad APIs, Open Banking, and Machine Learning to deliver real-time financial intelligence.

---

## Core Modules

### 1. Multi-Bank Aggregation

- Unified dashboard across all accounts
- User-defined account labeling (Personal, Business, Savings, etc.)
- Real-time transaction synchronization

### 2. Intelligent Cash Flow Manager

- AI-powered forecasting (30/60/90 days)
- Virtual accounts via Squad
- Automated reconciliation via webhooks

### 3. AI Credit Engine

- Alternative credit scoring using behavioral data
- Random Forest model
- Instant loan disbursement via Squad

### 4. Fraud Detection System

- Variational Autoencoder (VAE) anomaly detection
- Graph-based fraud pattern detection
- Real-time transaction blocking

---

## Tech Stack

Frontend:

- React / React Native

Backend:

- Node.js / FastAPI

Machine Learning:

- TensorFlow / PyTorch / Scikit-learn

Infrastructure:

- Docker / Kubernetes

Integrations:

- Squad API (payments, transfers, accounts)
- Mono (open banking)
- KYC Providers (BVN/NIN verification)

---

## System Architecture

See:

- docs/architecture/system_diagram.png
- docs/architecture/data_flow.png

---

## API Integrations

- Squad APIs (Virtual Accounts, Transfers, Subscriptions)
- Mono Connect SDK
- KYC Verification APIs

Postman Collection:
docs/api/squad_postman_collection.json

---

## Machine Learning Models

| Model         | Purpose                 |
| ------------- | ----------------------- |
| ARIMA / LSTM  | Cash flow forecasting   |
| Random Forest | Credit scoring          |
| VAE           | Fraud anomaly detection |
| GNN           | Fraud network analysis  |

Model cards available in:
docs/ml/model_cards/

---

## Getting Started

```bash
git clone https://github.com/your-team/fincore-ai
cd fincore-ai
cp .env.example .env
docker-compose up
```

---

## Demo Flow

1. User onboarding (BVN/NIN)
2. Bank account linking (Mono)
3. Dashboard aggregation
4. Cash flow prediction
5. Credit scoring + loan disbursement
6. Fraud detection in real time

---

## Documentation

- PRD → docs/PRD/
- Architecture → docs/architecture/
- ML Models → docs/ml/
- API Specs → docs/api/

---

## Team

Built for GTCo Squad Hackathon 3.0

---

## License

MIT License
