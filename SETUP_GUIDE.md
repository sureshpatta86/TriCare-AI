# TriCare AI - Complete Setup Guide

This guide will walk you through setting up the complete TriCare AI application from scratch.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.10 or higher installed
- [ ] Node.js 18 or higher installed
- [ ] Git installed
- [ ] Azure OpenAI API access (with GPT-4 deployment)
- [ ] Text editor or IDE (VS Code recommended)
- [ ] Terminal/Command Line access

## 🎯 Setup Steps

### Step 1: Clone and Navigate

```bash
cd /Users/sureshpatta/Developer/Projects/tricare
```

You should see:
- `frontend/` directory
- `backend/` directory
- `README.md`
- `tricare_dev_docs.md`

### Step 2: Backend Setup

#### 2.1 Install Python Dependencies

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows
```

#### 2.2 Install Requirements

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- FastAPI and Uvicorn
- LangChain, LangGraph, and Azure OpenAI
- PyTorch and torchvision
- Document processing libraries (PyPDF2, pytesseract, pydicom)
- All other dependencies

#### 2.3 Install Tesseract OCR

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install and add to PATH

#### 2.4 Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your actual values
nano .env  # or use your preferred editor
```

**Required values:**
```
AZURE_OPENAI_API_KEY=your_actual_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_VISION_DEPLOYMENT=gpt-4-vision
```

Get these from your Azure Portal → Azure OpenAI Service.

#### 2.5 Start Backend

```bash
# From the backend directory
python app/main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ **Test it**: Open http://localhost:8000/api/health in your browser

Expected response:
```json
{
  "status": "healthy",
  "app_name": "TriCare AI",
  "version": "1.0.0",
  "timestamp": "2025-10-18T..."
}
```

Keep this terminal open and running!

### Step 3: Frontend Setup

Open a NEW terminal window/tab.

#### 3.1 Navigate to Frontend

```bash
cd /Users/sureshpatta/Developer/Projects/tricare/frontend
```

#### 3.2 Install Dependencies

```bash
npm install
# This will take a few minutes
```

This installs:
- Next.js 14 and React 18
- TypeScript
- Tailwind CSS
- Axios, react-hook-form, zod
- All UI dependencies

#### 3.3 Configure Environment

```bash
# Copy the example env file
cp .env.local.example .env.local

# Edit if needed (default should work)
nano .env.local
```

Default values:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_ANALYTICS=false
```

#### 3.4 Start Frontend

```bash
npm run dev
```

You should see:
```
  ▲ Next.js 14.x
  - Local:        http://localhost:3000
  - Ready in X.Xs
```

✅ **Test it**: Open http://localhost:3000 in your browser

You should see the TriCare AI landing page!

### Step 4: Verify Everything Works

#### 4.1 Check All Pages

Visit these URLs and verify they load without errors:

1. http://localhost:3000 - Landing page ✅
2. http://localhost:3000/reports - Report simplifier ✅
3. http://localhost:3000/symptoms - Symptom router ✅
4. http://localhost:3000/imaging - Imaging pre-screen ✅

#### 4.2 Check API Endpoints

Visit http://localhost:8000/api/docs

You should see the interactive API documentation (Swagger UI) with:
- Health endpoints
- Reports endpoints
- Symptoms endpoints
- Imaging endpoints

#### 4.3 Test a Feature

Let's test the symptom router:

1. Go to http://localhost:3000/symptoms
2. Fill in the form:
   - Symptoms: "I have a persistent cough for 2 weeks"
   - Age: 30
   - Submit the form
3. You should see a response with specialist recommendation!

## 🐛 Troubleshooting

### Backend Issues

**Problem: `ModuleNotFoundError: No module named 'xyz'`**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
# Reinstall requirements
pip install -r requirements.txt
```

**Problem: `ImportError: pydicom`**
```bash
pip install pydicom
```

**Problem: `tesseract is not installed`**
- Install Tesseract OCR (see Step 2.3 above)
- Make sure it's in your PATH

**Problem: Azure OpenAI errors**
- Double-check your `.env` file has correct values
- Verify your Azure OpenAI deployment is active
- Check your API key is valid

### Frontend Issues

**Problem: `Cannot find module '@/...'`**
```bash
# Delete node_modules and reinstall
rm -rf node_modules
npm install
```

**Problem: Tailwind styles not working**
```bash
# Make sure globals.css is imported in layout.tsx
# Restart dev server
npm run dev
```

**Problem: API calls failing (CORS)**
- Make sure backend is running on port 8000
- Check `NEXT_PUBLIC_API_BASE_URL` in `.env.local`
- Verify CORS settings in backend `config.py`

## 📊 Project Status

After completing this setup, you should have:

✅ Backend running on http://localhost:8000
✅ Frontend running on http://localhost:3000
✅ All API endpoints functional
✅ All pages loading correctly
✅ Azure OpenAI integration working

## 🎓 Next Steps

Now that your setup is complete:

1. **Explore the Features**:
   - Try uploading a medical report (PDF or text)
   - Test the symptom router with various symptoms
   - Upload a chest X-ray image

2. **Read the Documentation**:
   - [Backend README](./backend/README.md)
   - [Frontend README](./frontend/README.md)
   - [Dev Docs](./tricare_dev_docs.md)

3. **Customize the Application**:
   - Modify the UI colors in `tailwind.config.ts`
   - Add new features or pages
   - Train your own ML model for imaging

4. **Deploy to Production**:
   - Backend → Azure Container Apps
   - Frontend → Vercel
   - See deployment guides in README files

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs in both terminal windows
3. Check the browser console for frontend errors (F12)
4. Review the API docs: http://localhost:8000/api/docs

## ⚠️ Important Reminders

- Keep the backend terminal running
- Keep the frontend terminal running
- Never commit `.env` or `.env.local` files
- This is an educational tool only - not for medical diagnosis

---

**You're all set! 🎉**

The TriCare AI application is now fully functional and ready for development or testing.
