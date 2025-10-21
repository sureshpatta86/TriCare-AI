# TriCare AI

<div align="center">

![TriCare AI Logo](https://via.placeholder.com/150x150/0ea5e9/ffffff?text=TriCare+AI)

**AI-Powered Medical Triage and Education Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14+](https://img.shields.io/badge/next.js-14+-black.svg)](https://nextjs.org/)

[Features](#features) • [Architecture](#architecture) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Disclaimer](#disclaimer)

</div>

---

## 🏥 Overview

TriCare AI is a comprehensive medical information platform that helps users understand complex medical data through AI-powered analysis and plain-language explanations. Built with cutting-edge technologies including GPT-4, LangChain, and PyTorch.

### ⚠️ Important Notice

**THIS IS AN EDUCATIONAL TOOL ONLY**
- NOT a medical device
- NOT for diagnostic purposes
- NOT a substitute for professional medical advice
- Always consult qualified healthcare providers for medical decisions

## ✨ Features

### 1. 📄 Medical Report Simplifier

Transform complex medical reports into patient-friendly language.

- **Upload**: PDF, images, or paste text
- **Extract**: OCR for scanned documents
- **Simplify**: GPT-4 powered plain-language summaries
- **Highlight**: Key findings with severity indicators
- **Recommend**: Specialist consultations

### 2. 🩺 Symptom Router

Intelligent symptom analysis and healthcare provider routing.

- **Describe**: Free-text symptom input
- **Analyze**: LangGraph multi-step reasoning workflow
- **Assess**: Urgency level classification
- **Route**: Appropriate specialist recommendation
- **Prepare**: Appointment preparation tips

### 3. 🔬 X-ray Pre-Screen

AI-powered preliminary analysis of medical imaging.

- **Upload**: X-rays, CT scans, DICOM files
- **Analyze**: MobileNetV2 ML model or GPT Vision
- **Visualize**: Grad-CAM heatmap overlays
- **Explain**: Plain-language findings
- **Guide**: Next steps and specialist referrals

## � Latest Updates - Phase 1 Production Enhancements

### Backend Improvements
- ✅ **Rate Limiting**: Protects API endpoints (10/min imaging, 20/min reports, 30/min symptoms)
- ✅ **Request Tracking**: UUID correlation IDs for every request
- ✅ **Enhanced Error Handling**: Structured responses with timestamps and correlation IDs
- ✅ **File Validation**: Size limits and type checking for security
- ✅ **Structured Logging**: Comprehensive logging with request tracking

### Frontend Improvements
- ✅ **ProgressIndicator Component**: Visual step-by-step progress tracking
- ✅ **Correlation ID Display**: Support tracking IDs shown in error messages
- ✅ **Enhanced Error Messages**: Specific, actionable feedback for users
- ✅ **Loading States**: Professional multi-step progress visualization
- ✅ **Dark Mode**: Full dark mode support across all features

### Security & Reliability
- Input validation and sanitization
- Rate limit protection against abuse
- Correlation IDs for debugging and support
- Comprehensive error tracking
- File size and type validation

See [PHASE1_IMPLEMENTATION.md](PHASE1_IMPLEMENTATION.md) and [FRONTEND_ENHANCEMENTS.md](FRONTEND_ENHANCEMENTS.md) for details.

## �🏗️ Architecture

```
┌─────────────────────────────────────┐
│     Next.js Frontend (Port 3000)    │
│  TypeScript + Tailwind CSS + React  │
└──────────────┬──────────────────────┘
               │ REST API
               │
┌──────────────▼──────────────────────┐
│    FastAPI Backend (Port 8000)      │
│  Python + LangChain + LangGraph     │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌─────▼──────┐
│ Azure OpenAI│  │  ML Models │
│   GPT-4/5   │  │ MobileNetV2│
└─────────────┘  └────────────┘
```

### Tech Stack

**Frontend:**
- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS
- Axios, react-hook-form, zod

**Backend:**
- FastAPI
- LangChain + LangGraph
- Azure OpenAI (GPT-4, GPT-4 Vision)
- PyTorch + torchvision
- PyPDF2, pytesseract, pydicom

**Infrastructure:**
- Docker
- Vercel (Frontend)
- Azure Container Apps (Backend)
- Azure Key Vault (Secrets)

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Azure OpenAI API access
- Docker (optional)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/tricare-ai.git
cd tricare-ai
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR
# macOS: brew install tesseract
# Ubuntu: sudo apt-get install tesseract-ocr

# Configure environment
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# Run backend
python app/main.py
```

Backend will be available at http://localhost:8000

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with API URL

# Run frontend
npm run dev
```

Frontend will be available at http://localhost:3000

### 4. Access Application

Open http://localhost:3000 in your browser and start exploring!

## 📚 Documentation

### API Documentation

Once the backend is running, visit:
- Interactive Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Project Documentation

- [Backend README](./backend/README.md) - Backend setup and API details
- [Frontend README](./frontend/README.md) - Frontend setup and components
- [Development Guide](./tricare_dev_docs.md) - Complete development documentation

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
pytest --cov=app tests/  # With coverage
```

### Frontend Tests

```bash
cd frontend
npm run lint
npm run type-check
```

## 🐳 Docker Deployment

### Backend

```bash
cd backend
docker build -t tricare-backend .
docker run -p 8000:8000 --env-file .env tricare-backend
```

### Frontend

```bash
cd frontend
docker build -t tricare-frontend .
docker run -p 3000:3000 tricare-frontend
```

## 📦 Project Structure

```
tricare-ai/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── services/     # Business logic
│   │   ├── models/       # ML models
│   │   ├── schemas/      # Pydantic models
│   │   └── graphs/       # LangGraph workflows
│   ├── tests/            # Backend tests
│   └── requirements.txt
│
├── frontend/             # Next.js frontend
│   ├── src/
│   │   ├── app/          # Pages and layouts
│   │   ├── components/   # React components
│   │   ├── lib/          # Utilities and API client
│   │   └── types/        # TypeScript types
│   └── package.json
│
└── tricare_dev_docs.md   # Complete development guide
```

## 🔒 Security

- All sensitive data stored in environment variables
- Input validation and sanitization
- Rate limiting on API endpoints
- HTTPS in production
- No medical data stored or logged

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Medical Disclaimer

**CRITICAL NOTICE:**

This application is designed for **educational purposes only** and is **NOT**:
- A medical device
- FDA approved
- Intended for diagnostic use
- A substitute for professional medical advice, diagnosis, or treatment

**Always:**
- Consult qualified healthcare professionals for medical decisions
- Seek immediate medical attention for emergencies (Call 911)
- Have all medical reports reviewed by licensed practitioners
- Get imaging reviewed by qualified radiologists

The developers and contributors assume no liability for any medical decisions made based on information from this application.

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/tricare-ai/issues)
- **Email**: support@tricare-ai.com
- **Documentation**: [Full Documentation](./tricare_dev_docs.md)

## 🙏 Acknowledgments

- Powered by Azure OpenAI (GPT-4)
- Built with LangChain and LangGraph
- UI inspired by modern healthcare platforms
- Medical datasets: NIH ChestX-ray14

---

<div align="center">

**Built with ❤️ for medical education**

[⬆ back to top](#tricare-ai)

</div>
