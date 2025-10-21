# TriCare AI - Backend

FastAPI backend for the TriCare AI medical triage and education platform.

## Features

- **Medical Report Simplifier**: PDF/OCR extraction with LangChain and GPT-4 summarization
- **Symptom Router**: LangGraph workflow for intelligent symptom analysis and specialist routing
- **X-ray Pre-Screen**: MobileNetV2 ML model for chest X-ray classification with Grad-CAM visualization
- **Azure OpenAI Integration**: Powered by GPT-4 and GPT-4 Vision

## Tech Stack

- **Framework**: FastAPI
- **AI/ML**: LangChain, LangGraph, PyTorch, Azure OpenAI
- **Document Processing**: PyPDF2, pytesseract, pydicom
- **Validation**: Pydantic v2
- **Testing**: pytest

## Prerequisites

- Python 3.10 or higher
- Azure OpenAI API access
- Tesseract OCR (for image text extraction)

## Installation

### 1. Create Virtual Environment

```bash
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required environment variables:
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Your GPT-4 deployment name
- `AZURE_OPENAI_VISION_DEPLOYMENT`: Your GPT-4 Vision deployment name

## Running the Application

### Development Mode

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or simply:

```bash
python app/main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health Check
```
GET /api/health
```

### Medical Report Simplifier
```
POST /api/reports/simplify
GET /api/reports/supported-formats
```

### Symptom Router
```
POST /api/symptoms/route
GET /api/symptoms/urgency-levels
```

### Imaging Pre-Screen
```
POST /api/imaging/prescreen
GET /api/imaging/supported-formats
```

## ML Model Setup

The X-ray pre-screen feature requires a trained MobileNetV2 model. 

### Option 1: Use Pre-trained Model

Place your trained model weights at:
```
app/models/weights/mobilenetv2_xray.pth
```

### Option 2: Train Your Own

1. Prepare a chest X-ray dataset (e.g., ChestX-ray14, NIH dataset)
2. Fine-tune MobileNetV2 for binary classification (normal/abnormal)
3. Save the model weights to the path above

### Option 3: Use GPT Vision Fallback

If no ML model is available, the system automatically falls back to GPT-4 Vision analysis.

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app tests/
```

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Configuration management
│   ├── api/
│   │   └── routes/             # API route handlers
│   ├── services/               # Business logic services
│   ├── models/
│   │   └── ml_models/          # ML model loaders
│   ├── schemas/                # Pydantic models
│   ├── utils/                  # Utility functions
│   └── graphs/                 # LangGraph workflows
├── tests/                      # Test files
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
└── README.md                   # This file
```

## Docker Deployment

Build the Docker image:

```bash
docker build -t tricare-backend .
```

Run the container:

```bash
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name tricare-backend \
  tricare-backend
```

## Important Disclaimers

⚠️ **CRITICAL**: This application is for EDUCATIONAL PURPOSES ONLY.

- NOT a medical device
- NOT for diagnostic use
- NOT a replacement for professional medical advice
- Always consult licensed healthcare providers for medical decisions

## Security Considerations

- Never commit `.env` files or API keys
- Use Azure Key Vault for production secrets
- Implement rate limiting for production deployments
- Validate and sanitize all user inputs
- Use HTTPS in production

## Support

For issues or questions:
- Create an issue on GitHub
- Email: support@tricare-ai.com

## License

MIT License - See LICENSE file for details

---

Built with ❤️ for medical education
