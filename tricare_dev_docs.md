# TriCare AI - Complete Development Guide

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Development Environment Setup](#development-environment-setup)
6. [Backend Development](#backend-development)
7. [Frontend Development](#frontend-development)
8. [AI/ML Implementation](#aiml-implementation)
9. [Integration Guidelines](#integration-guidelines)
10. [Deployment Strategy](#deployment-strategy)
11. [Testing Strategy](#testing-strategy)
12. [Security & Compliance](#security--compliance)
13. [Monitoring & Maintenance](#monitoring--maintenance)

---

## 1. Project Overview

### Purpose
TriCare AI is a medical triage and education web application that helps users understand medical information and provides preliminary guidance (NOT diagnostic advice).

### Core Features

#### Feature 1: Medical Report Simplifier
- **Input**: PDF, image, or pasted text of medical reports
- **Process**: Extract → Structure → Simplify with GPT
- **Output**: 
  - Plain-language summary
  - "What it means" explanation
  - Actionable next steps
  - Which specialist to consult

#### Feature 2: Symptom-to-Specialist Router
- **Input**: Free-text symptom description + metadata (age/sex + flags)
- **Process**: Prompted reasoning with LangGraph workflow
- **Output**:
  - Specialist recommendation
  - Urgency level (self-care / routine / same-day / ER)
  - Red flags to monitor
  - Suggested tests/preparations

#### Feature 3: X-ray/CT Pre-Screen
- **Input**: DICOM or PNG/JPG medical images
- **Process**: 
  - ML model inference (normal vs abnormal classification)
  - If abnormal detected → GPT generates explanation
- **Output**:
  - Prediction (normal/abnormal) + confidence
  - Heatmap (Grad-CAM if available)
  - GPT explanation in plain language
  - Recommended next steps
- **Fallback**: If model unavailable, use GPT Vision with disclaimer banner

### Critical Disclaimers
- Display prominently: "Not a medical device, not diagnostic advice"
- "For education and triage preview only"
- "Always consult a licensed clinician"

---

## 2. System Architecture

### Architecture Pattern: Separated Frontend + Backend

```
┌─────────────────────────────────────────┐
│         Next.js Frontend                │
│  (TypeScript + Tailwind CSS)           │
│  - UI Components                        │
│  - State Management                     │
│  - File Upload Handling                 │
│  - Result Visualization                 │
└──────────────┬──────────────────────────┘
               │
               │ REST/HTTP API
               │
┌──────────────▼──────────────────────────┐
│         Python FastAPI Backend          │
│  - API Endpoints                        │
│  - Request Validation                   │
│  - File Processing                      │
│  - LangChain/LangGraph Orchestration   │
└──────────────┬──────────────────────────┘
               │
      ┌────────┴────────┐
      │                 │
┌─────▼─────┐    ┌─────▼──────┐
│  Azure    │    │  ML Model  │
│  OpenAI   │    │ MobileNetV2│
│  GPT-4.1  │    │  (Local)   │
│  GPT-5    │    └────────────┘
└───────────┘
```

### Data Flow

#### Flow 1: Medical Report Simplifier
1. User uploads PDF/image/text via Next.js
2. Frontend sends to `/api/reports/simplify`
3. Backend extracts text (PyPDF2/pytesseract)
4. LangChain loads document → splits → structures
5. Azure OpenAI generates simplified summary
6. Backend returns structured JSON response
7. Frontend renders with components

#### Flow 2: Symptom Router
1. User enters symptoms + metadata
2. Frontend sends to `/api/symptoms/route`
3. LangGraph workflow begins:
   - State: symptom extraction
   - State: urgency assessment
   - State: specialist matching
   - State: generate recommendations
4. Azure OpenAI processes at each state
5. Return structured specialist guidance
6. Frontend displays recommendation card

#### Flow 3: X-ray Pre-Screen
1. User uploads DICOM/image
2. Frontend sends to `/api/imaging/prescreen`
3. Backend preprocesses image for model
4. MobileNetV2 inference → prediction + confidence
5. If abnormal: Generate Grad-CAM heatmap
6. Azure OpenAI explains findings in plain language
7. Return prediction + heatmap + explanation
8. Frontend overlays heatmap on original image

---

## 3. Technology Stack

### Frontend Stack
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (optional but recommended)
- **State Management**: React Context API + Zustand (for complex state)
- **File Upload**: react-dropzone
- **Image Display**: react-image-gallery or custom canvas
- **PDF Display**: react-pdf
- **HTTP Client**: Axios or native fetch
- **Form Handling**: react-hook-form + zod validation

### Backend Stack
- **Framework**: FastAPI (Python 3.10+)
- **AI Orchestration**: LangChain + LangGraph
- **LLM Integration**: langchain-openai (Azure OpenAI)
- **ML Framework**: PyTorch (for MobileNetV2)
- **ML Utilities**: torchvision, opencv-python, Pillow
- **Document Processing**: PyPDF2, pytesseract (OCR), python-docx
- **DICOM Handling**: pydicom
- **Validation**: Pydantic v2
- **Environment**: python-dotenv
- **Testing**: pytest + pytest-asyncio
- **CORS**: fastapi-cors

### AI/ML Components
- **LLM**: Azure OpenAI GPT-4.1 or GPT-5 Chat models
- **Vision Model**: Azure OpenAI GPT-4 Vision (fallback for X-ray)
- **Local ML**: MobileNetV2 fine-tuned on chest X-ray dataset
- **Heatmap Generation**: Grad-CAM (gradient-weighted class activation mapping)

### DevOps & Infrastructure
- **Frontend Hosting**: Vercel (recommended) or Azure Static Web Apps
- **Backend Hosting**: Azure Container Apps or Azure App Service
- **ML Model Storage**: Azure Blob Storage (model weights)
- **Secrets Management**: Azure Key Vault
- **Monitoring**: Azure Application Insights
- **CI/CD**: GitHub Actions

---

## 4. Project Structure

### Frontend Structure (Next.js)
```
tricare-frontend/
├── public/
│   ├── images/
│   └── icons/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx (landing page)
│   │   ├── reports/
│   │   │   └── page.tsx (medical report simplifier)
│   │   ├── symptoms/
│   │   │   └── page.tsx (symptom router)
│   │   ├── imaging/
│   │   │   └── page.tsx (x-ray pre-screen)
│   │   └── api/ (if using Next.js API routes as proxy)
│   ├── components/
│   │   ├── ui/ (shadcn components)
│   │   ├── shared/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── DisclaimerBanner.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   ├── reports/
│   │   │   ├── FileUploader.tsx
│   │   │   ├── ReportDisplay.tsx
│   │   │   └── SimplifiedSummary.tsx
│   │   ├── symptoms/
│   │   │   ├── SymptomForm.tsx
│   │   │   ├── SpecialistCard.tsx
│   │   │   └── UrgencyBadge.tsx
│   │   └── imaging/
│   │       ├── ImageUploader.tsx
│   │       ├── HeatmapOverlay.tsx
│   │       ├── PredictionDisplay.tsx
│   │       └── ExplanationPanel.tsx
│   ├── lib/
│   │   ├── api-client.ts (API wrapper functions)
│   │   ├── utils.ts
│   │   └── constants.ts
│   ├── types/
│   │   ├── reports.ts
│   │   ├── symptoms.ts
│   │   └── imaging.ts
│   ├── hooks/
│   │   ├── useFileUpload.ts
│   │   └── useApi.ts
│   └── styles/
│       └── globals.css
├── .env.local
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

### Backend Structure (Python/FastAPI)
```
tricare-backend/
├── app/
│   ├── main.py (FastAPI app initialization)
│   ├── config.py (configuration management)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── reports.py (report simplifier endpoints)
│   │   │   ├── symptoms.py (symptom router endpoints)
│   │   │   ├── imaging.py (x-ray pre-screen endpoints)
│   │   │   └── health.py (health check endpoint)
│   │   └── dependencies.py (shared dependencies)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_processor.py (PDF/OCR extraction)
│   │   ├── report_simplifier.py (LangChain report logic)
│   │   ├── symptom_router.py (LangGraph symptom workflow)
│   │   ├── imaging_analyzer.py (ML model + GPT integration)
│   │   └── azure_openai_service.py (Azure OpenAI wrapper)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ml_models/ (ML model loading and inference)
│   │   │   ├── mobilenetv2_loader.py
│   │   │   ├── gradcam.py
│   │   │   └── image_preprocessor.py
│   │   └── weights/ (store model weights here or fetch from blob)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── reports.py (Pydantic models for reports)
│   │   ├── symptoms.py (Pydantic models for symptoms)
│   │   └── imaging.py (Pydantic models for imaging)
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_helpers.py
│   │   ├── validation.py
│   │   └── logging_config.py
│   └── graphs/ (LangGraph state definitions)
│       ├── __init__.py
│       └── symptom_workflow.py
├── tests/
│   ├── __init__.py
│   ├── test_reports.py
│   ├── test_symptoms.py
│   └── test_imaging.py
├── .env
├── .env.example
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 5. Development Environment Setup

### Prerequisites
- Node.js 18+ and npm/pnpm
- Python 3.10+
- Azure subscription with OpenAI service
- Git
- Docker (optional, for containerization)

### Step 1: Clone Repository
Initialize two separate repositories or a monorepo:
```
Option A: Monorepo
tricare-ai/
├── frontend/
└── backend/

Option B: Separate repos
tricare-frontend/
tricare-backend/
```

### Step 2: Frontend Setup

#### Initialize Next.js Project
1. Create Next.js app with TypeScript and Tailwind
2. Configure App Router (default in Next.js 14+)
3. Install core dependencies:
   - react-dropzone
   - axios
   - zustand
   - react-hook-form
   - zod
   - @radix-ui/react-* (via shadcn/ui)
   - lucide-react (icons)
   - react-pdf
   - clsx, tailwind-merge

#### Setup Tailwind Configuration
1. Extend theme with medical/healthcare color palette
2. Add custom utilities for medical UI patterns
3. Configure content paths for component scanning

#### Environment Variables
Create `.env.local`:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_ANALYTICS=false
```

### Step 3: Backend Setup

#### Create Virtual Environment
1. Create Python virtual environment
2. Activate virtual environment

#### Install Dependencies
Create `requirements.txt` with:
- fastapi
- uvicorn[standard]
- langchain
- langchain-openai
- langgraph
- openai (for Azure integration)
- python-multipart (file uploads)
- python-dotenv
- pydantic
- pydantic-settings
- PyPDF2
- pytesseract
- python-docx
- Pillow
- opencv-python
- pydicom
- torch
- torchvision
- pytest
- pytest-asyncio
- httpx

Install all dependencies in virtual environment.

#### Environment Variables
Create `.env`:
```
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-deployment-name
AZURE_OPENAI_VISION_DEPLOYMENT=gpt-4-vision-deployment-name

MODEL_WEIGHTS_PATH=./app/models/weights/
ENABLE_ML_MODEL=true
ENABLE_GRADCAM=true

MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=pdf,png,jpg,jpeg,dcm

LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

#### Setup Tesseract OCR
1. Install Tesseract OCR system dependency
2. For Windows: Download installer from GitHub
3. For Linux: Install via package manager
4. For macOS: Install via Homebrew
5. Set TESSERACT_PATH in environment if needed

---

## 6. Backend Development

### Phase 1: FastAPI Foundation

#### Step 1: Initialize FastAPI Application
In `main.py`:
1. Create FastAPI app instance
2. Configure CORS middleware with frontend origin
3. Add exception handlers for common errors
4. Add request logging middleware
5. Include routers from each feature module
6. Add startup event handler to load ML model
7. Add health check endpoint

#### Step 2: Configuration Management
In `config.py`:
1. Create Pydantic Settings class
2. Load environment variables
3. Validate required configurations
4. Set up logging configuration
5. Define constants (max file sizes, allowed types, etc.)

#### Step 3: Create Base Schemas
In `schemas/`:
1. Define Pydantic models for API requests/responses
2. Include validation rules (file size, formats)
3. Create error response schemas
4. Add documentation strings for OpenAPI

### Phase 2: Document Processing Service

#### Medical Report Simplifier Implementation

**Step 1: Document Extraction**
In `services/document_processor.py`:
1. Create function to handle PDF extraction using PyPDF2
2. Create function for image OCR using pytesseract
3. Create function for plain text processing
4. Add error handling for corrupted files
5. Implement text cleaning and normalization

**Step 2: LangChain Integration**
In `services/report_simplifier.py`:
1. Initialize Azure OpenAI ChatModel with LangChain
2. Create document text splitter for long reports
3. Define prompt template for report simplification:
   - System prompt: "You are a medical translator converting complex reports to plain language"
   - Include structure: Summary, What it means, Next steps, Specialist
4. Create LangChain chain: document → split → summarize → structure
5. Implement structured output using JSON mode or output parsers
6. Add retry logic for API failures

**Step 3: API Endpoint**
In `api/routes/reports.py`:
1. Create POST `/api/reports/simplify` endpoint
2. Accept file upload (multipart/form-data)
3. Validate file type and size
4. Call document processor
5. Call report simplifier service
6. Return structured JSON response
7. Add error handling and logging

### Phase 3: Symptom Router with LangGraph

#### LangGraph Workflow Design

**Step 1: Define State**
In `graphs/symptom_workflow.py`:
1. Create State class with TypedDict:
   - symptoms: str
   - age: int
   - sex: str
   - flags: List[str]
   - urgency: str
   - specialist: str
   - reasoning: str
   - red_flags: List[str]
   - suggested_tests: List[str]

**Step 2: Create Workflow Nodes**
1. Node: extract_key_symptoms
   - Extract main symptoms from free text
   - Categorize by body system
   
2. Node: assess_urgency
   - Determine urgency level (self-care/routine/same-day/ER)
   - Consider red flag keywords (chest pain, difficulty breathing, etc.)
   - Use GPT-5 Chat with structured output
   
3. Node: determine_specialist
   - Match symptoms to specialist type
   - Consider age/sex specific conditions
   - Return specialist recommendation
   
4. Node: generate_recommendations
   - Create actionable next steps
   - List red flags to monitor
   - Suggest preparation for appointment
   - Recommend tests if applicable

**Step 3: Build Graph**
1. Create StateGraph with State class
2. Add all nodes to graph
3. Define edges:
   - START → extract_key_symptoms
   - extract_key_symptoms → assess_urgency
   - assess_urgency → determine_specialist
   - determine_specialist → generate_recommendations
   - generate_recommendations → END
4. Compile graph

**Step 4: Service Implementation**
In `services/symptom_router.py`:
1. Initialize compiled graph
2. Create function to run workflow with input
3. Handle streaming updates (optional)
4. Extract final state and format response
5. Add error handling for incomplete workflow

**Step 5: API Endpoint**
In `api/routes/symptoms.py`:
1. Create POST `/api/symptoms/route` endpoint
2. Accept JSON payload with symptoms, age, sex, flags
3. Validate input data
4. Run LangGraph workflow
5. Return structured response with specialist, urgency, recommendations
6. Add comprehensive error handling

### Phase 4: X-ray/CT Pre-Screen with ML

#### ML Model Setup

**Step 1: Model Preparation**
In `models/ml_models/mobilenetv2_loader.py`:
1. Define MobileNetV2 architecture for binary classification
2. Load pre-trained weights from file or Azure Blob
3. Set model to evaluation mode
4. Move model to appropriate device (CPU/GPU)
5. Create singleton pattern for model loading

**Step 2: Image Preprocessing**
In `models/ml_models/image_preprocessor.py`:
1. Create preprocessing pipeline:
   - Resize to model input size (224x224 typically)
   - Convert to RGB if grayscale
   - Normalize with ImageNet stats or custom stats
   - Convert to tensor
2. Handle DICOM files:
   - Extract pixel data from DICOM
   - Apply windowing if necessary
   - Convert to appropriate format

**Step 3: Grad-CAM Implementation**
In `models/ml_models/gradcam.py`:
1. Implement Grad-CAM algorithm:
   - Hook into last convolutional layer
   - Compute gradients for target class
   - Generate weighted activation map
   - Upsample to original image size
   - Create heatmap overlay
2. Return heatmap as base64 image

#### Integration with GPT

**Step 1: Imaging Analyzer Service**
In `services/imaging_analyzer.py`:
1. Create function for ML inference:
   - Load and preprocess image
   - Run model inference
   - Get prediction and confidence
   - Generate Grad-CAM if abnormal detected
   
2. Create function for GPT explanation:
   - Use Azure OpenAI GPT-4 Chat
   - Prompt template: "Explain this X-ray finding in plain language for a patient"
   - Provide prediction, confidence, and body region
   - Generate actionable next steps
   - Include disclaimer reminder

3. Create fallback function:
   - If ML model unavailable, use GPT Vision
   - Send image to GPT-4 Vision
   - Request analysis with clear medical disclaimer
   - Add banner: "Using Vision model - not a diagnostic tool"

**Step 2: API Endpoint**
In `api/routes/imaging.py`:
1. Create POST `/api/imaging/prescreen` endpoint
2. Accept image upload (DICOM, PNG, JPG)
3. Validate file type and size
4. Run ML model inference
5. Generate heatmap if abnormal
6. Get GPT explanation
7. Return structured response:
   - prediction: str
   - confidence: float
   - heatmap: base64 image
   - explanation: str
   - next_steps: List[str]
8. Handle fallback to Vision model
9. Add comprehensive error handling

### Phase 5: Utilities and Helpers

#### File Handling
In `utils/file_helpers.py`:
1. Create functions for:
   - Temporary file management
   - File type validation
   - File size checking
   - Safe file deletion
   - Base64 encoding/decoding

#### Validation Utilities
In `utils/validation.py`:
1. Create custom validators for:
   - Medical terminology sanitization
   - Age range validation
   - File format verification
   - Input length limits

#### Logging Setup
In `utils/logging_config.py`:
1. Configure structured logging
2. Set up different log levels for dev/prod
3. Add request ID tracking
4. Configure log rotation

---

## 7. Frontend Development

### Phase 1: Core Setup

#### Step 1: Layout and Navigation
In `app/layout.tsx`:
1. Create root layout with:
   - Metadata (title, description, OpenGraph)
   - Global styles import
   - Disclaimer banner (always visible)
   - Header with navigation
   - Footer with legal links
2. Use Tailwind for responsive design

In `components/shared/Header.tsx`:
1. Create navigation with links to three features
2. Add logo/branding
3. Mobile-responsive hamburger menu
4. Sticky header on scroll

In `components/shared/DisclaimerBanner.tsx`:
1. Prominent banner at top of all pages
2. Text: "Not a medical device. Not diagnostic advice. For education and triage preview only."
3. Non-dismissible
4. Accessible color contrast

#### Step 2: API Client Setup
In `lib/api-client.ts`:
1. Create Axios instance with base URL
2. Add request interceptors for auth (if needed)
3. Add response interceptors for error handling
4. Create typed functions for each endpoint:
   - `simplifyReport(file: File)`
   - `routeSymptoms(data: SymptomData)`
   - `prescreenImage(file: File)`
5. Handle loading states and errors

#### Step 3: Type Definitions
In `types/`:
1. Define TypeScript interfaces matching backend schemas
2. Create types for API responses
3. Add types for component props
4. Use zod for runtime validation

### Phase 2: Medical Report Simplifier UI

#### Step 1: Upload Component
In `components/reports/FileUploader.tsx`:
1. Use react-dropzone for file upload
2. Accept PDF, images, or allow paste text
3. Show file preview before upload
4. Display file size and type
5. Add upload progress indicator
6. Handle drag-and-drop
7. Clear file button

#### Step 2: Main Page
In `app/reports/page.tsx`:
1. Create page layout with uploader
2. Add state management for:
   - Uploaded file
   - Loading state
   - API response
   - Error messages
3. Call API on file upload
4. Show loading spinner during processing
5. Render results when ready

#### Step 3: Results Display
In `components/reports/SimplifiedSummary.tsx`:
1. Display structured output:
   - Section: Plain-language summary (card)
   - Section: What it means (expandable)
   - Section: Next steps (actionable bullets)
   - Section: Recommended specialist (highlighted badge)
2. Add copy-to-clipboard functionality
3. Add download as PDF option
4. Use Tailwind for medical-themed styling
5. Ensure mobile responsiveness

### Phase 3: Symptom Router UI

#### Step 1: Symptom Form
In `components/symptoms/SymptomForm.tsx`:
1. Create form with react-hook-form:
   - Large text area for symptom description
   - Age input (number)
   - Sex selection (dropdown or radio)
   - Checkboxes for flags:
     - Pregnant?
     - Chronic disease?
     - Immunocompromised?
     - Taking medications?
2. Add real-time validation with zod
3. Show character count for symptoms
4. Add helpful placeholder text
5. Submit button with loading state

#### Step 2: Main Page
In `app/symptoms/page.tsx`:
1. Render symptom form
2. Handle form submission
3. Call API with form data
4. Manage loading and error states
5. Show results when ready

#### Step 3: Results Display
In `components/symptoms/SpecialistCard.tsx`:
1. Display specialist recommendation:
   - Specialist type (large, bold)
   - Icon for specialist
   - Brief reasoning
2. Show urgency level with color-coded badge
3. List red flags to monitor
4. Show suggested tests/preparations
5. Add "Schedule appointment" CTA (external link or future feature)

In `components/symptoms/UrgencyBadge.tsx`:
1. Create color-coded badges:
   - Self-care: Green
   - Routine: Blue
   - Same-day: Orange
   - ER: Red
2. Include icon and clear text
3. Accessible color contrast

### Phase 4: X-ray Pre-Screen UI

#### Step 1: Image Upload
In `components/imaging/ImageUploader.tsx`:
1. Accept DICOM, PNG, JPG uploads
2. Show image preview after upload
3. Display file info (size, dimensions)
4. Add clear image button
5. Handle drag-and-drop
6. Show upload progress

#### Step 2: Main Page
In `app/imaging/page.tsx`:
1. Render image uploader
2. Display disclaimer banner (extra prominent)
3. Handle image submission
4. Manage loading state (this may take longer)
5. Show results when ready
6. Handle Vision model fallback with warning banner

#### Step 3: Results Display
In `components/imaging/HeatmapOverlay.tsx`:
1. Display original image
2. Overlay Grad-CAM heatmap with adjustable opacity
3. Add slider to adjust heatmap visibility
4. Show side-by-side view option
5. Ensure responsive canvas rendering

In `components/imaging/PredictionDisplay.tsx`:
1. Show prediction (Normal/Abnormal)
2. Display confidence percentage with visual indicator
3. Color-code based on confidence level
4. Show model metadata (model name, version)

In `components/imaging/ExplanationPanel.tsx`:
1. Display GPT explanation in readable format
2. Show next steps as actionable items
3. Emphasize disclaimer
4. Add "Consult specialist" CTA
5. Option to download report

### Phase 5: Shared Components

#### Loading States
In `components/shared/LoadingSpinner.tsx`:
1. Create spinner for async operations
2. Add loading text with context
3. Show estimated wait time for ML processing
4. Animated progress indicator

#### Error Handling
Create error boundary components:
1. Catch and display errors gracefully
2. Provide retry button
3. Show user-friendly error messages
4. Log errors for debugging

#### Toast Notifications
Add toast library (sonner or radix):
1. Success messages for completed actions
2. Error toasts for failed operations
3. Warning toasts for important info

---

## 8. AI/ML Implementation

### Azure OpenAI Configuration

#### Step 1: Azure Setup
1. Create Azure OpenAI resource in Azure Portal
2. Deploy required models:
   - GPT-4.1 or GPT-5 for text generation
   - GPT-4 Vision for image fallback
3. Note deployment names for each model
4. Get API key and endpoint
5. Configure API version (use latest stable)

#### Step 2: LangChain Integration
In `services/azure_openai_service.py`:
1. Create AzureChatOpenAI instance with configuration
2. Set model parameters:
   - temperature: 0.3 (for consistency)
   - max_tokens: 1000-2000
   - top_p: 0.9
3. Implement retry logic with exponential backoff
4. Add token counting for cost monitoring
5. Create different model instances for different tasks

#### Step 3: Prompt Engineering

**For Report Simplifier:**
```
System: You are a medical translator who converts complex medical reports into plain language for patients.

Instructions:
- Simplify medical terminology
- Maintain accuracy
- Structure output as: Summary, What it means, Next steps, Specialist
- Use bullet points for clarity
- Avoid medical jargon
- Be empathetic and clear

Output format: Return valid JSON with keys: summary, meaning, next_steps, specialist
```

**For Symptom Router (Multi-step):**

Node 1 (Extract symptoms):
```
System: Extract key symptoms from patient description.
Categorize by body system.
Return JSON: {symptoms: [], body_systems: []}
```

Node 2 (Assess urgency):
```
System: Assess urgency based on symptoms.
Consider red flags: chest pain, severe bleeding, difficulty breathing, altered consciousness.
Return JSON: {urgency: "self-care|routine|same-day|er", reasoning: "..."}
```

Node 3 (Determine specialist):
```
System: Match symptoms to appropriate medical specialist.
Consider: symptom type, body system, urgency, patient demographics.
Return JSON: {specialist: "...", justification: "..."}
```

Node 4 (Generate recommendations):
```
System: Provide actionable guidance.
Include: red flags to monitor, suggested tests, appointment preparation.
Return JSON: {red_flags: [], tests: [], preparation: [], disclaimer: "..."}
```

**For X-ray Explanation:**
```
System: You are explaining medical imaging findings to a patient.

Given:
- Prediction: {prediction}
- Confidence: {confidence}
- Region: {region}

Explain in plain language:
- What was found
- What it might mean
- What they should do next
- Emphasize this is preliminary, not diagnostic

Use simple language, be clear but not alarming.
```

### MobileNetV2 Fine-tuning Guide (Separate Task)

#### Dataset Preparation
1. Collect labeled chest X-ray dataset (e.g., ChestX-ray14, CheXpert)
2. Create train/validation/test splits (70/15/15)
3. Balance classes (normal vs abnormal)
4. Augment training data:
   - Random rotations (±10°)
   - Horizontal flips (not vertical for chest X-rays)
   - Brightness/contrast adjustments
   - Random crops

#### Model Training
1. Load pretrained MobileNetV2 from torchvision
2. Replace final classification layer for binary output
3. Freeze early layers, train final layers first
4. Unfreeze all and fine-tune with low learning rate
5. Use binary cross-entropy loss
6. Train with Adam optimizer
7. Early stopping on validation loss
8. Save best model checkpoint

#### Model Evaluation
1. Evaluate on test set
2. Calculate metrics: accuracy, precision, recall, F1, AUC-ROC
3. Analyze false positives/negatives
4. Generate confusion matrix
5. Validate clinical utility

#### Export for Deployment
1. Save model weights to .pth file
2. Test loading in inference environment
3. Optimize for inference (jit compile if needed)
4. Document model version and performance metrics

### Grad-CAM Implementation Details

#### Algorithm Steps
1. Forward pass: compute activations of last conv layer
2. Backward pass: compute gradients of target class w.r.t activations
3. Global average pooling of gradients
4. Weight activations by pooled gradients
5. Sum weighted activations
6. Apply ReLU to focus on positive influence
7. Normalize to [0, 1]
8. Upsample to input image size
9. Apply color map (jet or hot)
10. Overlay on original image with alpha blending

#### Visualization
1. Use OpenCV or Matplotlib for colormap
2. Save as PNG image
3. Convert to base64 for API response
4. Ensure heatmap highlights relevant regions

---

## 9. Integration Guidelines

### Frontend-Backend Integration

#### Step 1: API Contract Definition
1. Document all endpoints in OpenAPI/Swagger
2. Define request/response schemas
3. Specify error codes and messages
4. Version API (e.g., /api/v1/)

#### Step 2: Error Handling Strategy
Frontend:
1. Catch network errors
2. Display user-friendly error messages
3. Implement retry for transient failures
4. Show detailed errors in dev mode only

Backend:
1. Return structured error responses
2. Use appropriate HTTP status codes
3. Log errors with context
4. Don't expose sensitive info in errors

#### Step 3: File Upload Flow
1. Frontend validates file before upload
2. Show upload progress
3. Backend validates again server-side
4. Stream large files if needed
5. Return processing status
6. Poll for long-running tasks (optional)

#### Step 4: State Management
1. Use Zustand for global state:
   - User session (if auth added)
   - Feature flags
   - API status
2. Use React state for component-level data
3. Use React Query or SWR for API caching (optional)

### CORS Configuration
Backend (FastAPI):
1. Add CORS middleware
2. Allow frontend origin(s)
3. Allow credentials if needed
4. Specify allowed methods (POST, GET)
5. Specify allowed headers

### Security Considerations
1. Validate all file uploads (type, size, content)
2. Sanitize user inputs
3. Rate limit API endpoints
4. Implement request timeouts
5. Use HTTPS in production
6. Store API keys securely (environment variables, Key Vault)
7. Add CSP headers
8. Implement CORS properly
9. Sanitize error messages

---

## 10. Deployment Strategy

### Backend Deployment (Azure Container Apps)

#### Step 1: Containerization
1. Create Dockerfile:
   - Base image: python:3.10-slim
   - Install system dependencies (tesseract)
   - Copy requirements.txt and install
   - Copy application code
   - Download model weights from Azure Blob on startup
   - Expose port 8000
   - CMD: uvicorn app.main:app --host 0.0.0.0 --port 8000

2. Build and test locally
3. Push to Azure Container Registry

#### Step 2: Azure Container Apps Setup
1. Create Azure Container App
2. Configure container:
   - Image from ACR
   - CPU: 1-2 cores
   - Memory: 2-4 GB (depending on ML model)
3. Set environment variables from Azure Key Vault
4. Enable auto-scaling (min: 1, max: 5 instances)
5. Configure health probes (endpoint: /health)
6. Set up ingress (HTTPS enabled)

#### Step 3: Model Storage
1. Upload model weights to Azure Blob Storage
2. Set up SAS token or managed identity
3. Download weights on container startup
4. Cache in container filesystem

### Frontend Deployment (Vercel)

#### Step 1: Vercel Setup
1. Connect GitHub repository to Vercel
2. Configure build settings:
   - Framework: Next.js
   - Build command: npm run build
   - Output directory: .next
3. Set environment variables (API URL)
4. Enable automatic deployments on push

#### Step 2: Domain Configuration
1. Add custom domain
2. Configure DNS
3. Enable SSL/TLS

### Database (Optional)
If adding user accounts or storing results:
1. Use Azure PostgreSQL or Cosmos DB
2. Store:
   - User accounts
   - Analysis history
   - Audit logs
3. Implement proper data retention policies
4. Ensure HIPAA compliance if handling PHI

### Monitoring & Logging

#### Application Insights Setup
1. Add Application Insights to backend
2. Track:
   - API request/response times
   - Error rates
   - Model inference latency
   - Token usage costs
3. Set up alerts for anomalies

#### Logging Strategy
1. Structured logging (JSON format)
2. Log levels: DEBUG, INFO, WARNING, ERROR
3. Include request IDs for tracing
4. Store logs in Azure Log Analytics
5. Set up log retention policies

### Backup & Disaster Recovery
1. Regular backups of configuration
2. Document deployment procedures
3. Test recovery process
4. Keep previous container versions
5. Blue-green deployment strategy

---

## 11. Testing Strategy

### Backend Testing

#### Unit Tests
In `tests/`:
1. Test each service function independently
2. Mock external dependencies (Azure OpenAI, ML model)
3. Test edge cases and error scenarios
4. Use pytest fixtures for common setups

Example test structure:
- `test_reports.py`: Test document extraction and simplification
- `test_symptoms.py`: Test LangGraph workflow steps
- `test_imaging.py`: Test ML inference and GPT integration

#### Integration Tests
1. Test full API endpoints with test client
2. Test file upload flows
3. Test error handling
4. Mock external APIs
5. Test rate limiting

#### ML Model Tests
1. Test model loading
2. Test inference on sample images
3. Validate output shapes and ranges
4. Test Grad-CAM generation
5. Benchmark inference time

### Frontend Testing

#### Component Tests
1. Use React Testing Library
2. Test each component in isolation
3. Test user interactions
4. Test conditional rendering
5. Test form validation

#### Integration Tests
1. Test complete user flows
2. Mock API responses
3. Test error states
4. Test loading states

#### E2E Tests (Optional)
Use Playwright or Cypress:
1. Test complete user journeys
2. Test across browsers
3. Test responsive design
4. Test accessibility

### Testing Checklist
- [ ] All API endpoints have tests
- [ ] Error handling is tested
- [ ] File upload validation works
- [ ] ML model inference is accurate
- [ ] GPT responses are structured correctly
- [ ] Frontend handles API errors gracefully
- [ ] Loading states display correctly
- [ ] Responsive design works on mobile
- [ ] Accessibility standards met
- [ ] Security validation in place

---

## 12. Security & Compliance

### Data Privacy (HIPAA Considerations)

#### Important Note
This application as designed is for education/triage preview only and should NOT store patient-identifiable health information (PHI) without proper HIPAA compliance infrastructure.

#### If Handling PHI
1. Ensure Business Associate Agreement with Azure
2. Use HIPAA-compliant Azure services
3. Encrypt data at rest and in transit
4. Implement access controls and audit logs
5. Follow minimum necessary principle
6. Conduct regular security assessments
7. Train all team members on HIPAA requirements

### Security Best Practices

#### Input Validation
1. Validate all file uploads (magic bytes, not just extension)
2. Limit file sizes
3. Sanitize text inputs
4. Use parameterized queries if using database
5. Validate content types

#### API Security
1. Implement rate limiting per IP
2. Add request timeouts
3. Use API keys for frontend-backend (if needed)
4. Validate tokens/sessions
5. Log authentication attempts

#### Secrets Management
1. Never commit secrets to git
2. Use Azure Key Vault for production
3. Use environment variables
4. Rotate keys regularly
5. Use managed identities where possible

#### Content Security
1. Implement CSP headers
2. Sanitize HTML if rendering user content
3. Prevent XSS attacks
4. Validate and sanitize redirects

### Compliance Requirements

#### Medical Device Disclaimer
Display on every page:
- "This is not a medical device"
- "Not for diagnostic use"
- "For educational and triage preview purposes only"
- "Always consult a licensed healthcare provider"

#### Terms of Service
Create clear terms including:
- Purpose and limitations
- No medical advice disclaimer
- Data handling policies
- User responsibilities
- Liability limitations

#### Privacy Policy
If collecting any data:
- What data is collected
- How it's used
- How long it's stored
- User rights (access, deletion)
- Cookie policy if applicable

---

## 13. Monitoring & Maintenance

### Performance Monitoring

#### Key Metrics to Track
1. API response times (p50, p95, p99)
2. ML model inference latency
3. Azure OpenAI API latency
4. Error rates by endpoint
5. Request volume
6. Token usage and costs
7. Container CPU/memory usage
8. Frontend load times

#### Alerts to Configure
1. Error rate > 5%
2. API response time > 5 seconds
3. Azure OpenAI API failures
4. Container memory > 90%
5. Unusual spike in traffic
6. Model inference failures

### Cost Monitoring
1. Track Azure OpenAI token usage
2. Monitor API call volumes
3. Track compute costs (Container Apps)
4. Set budget alerts
5. Optimize model calls (caching, batching)

### Maintenance Tasks

#### Regular Updates
1. Update dependencies monthly
2. Patch security vulnerabilities immediately
3. Update model weights if retrained
4. Review and update prompts based on performance
5. Monitor for LangChain/LangGraph updates

#### Model Maintenance
1. Monitor model performance metrics
2. Collect edge cases for retraining
3. A/B test model versions
4. Document model versions and performance
5. Retrain periodically with new data

#### User Feedback Loop
1. Add feedback mechanism in UI
2. Collect user ratings for AI outputs
3. Analyze common failure patterns
4. Iterate on prompts and workflows
5. Build dataset for future improvements

### Incident Response Plan
1. Define severity levels
2. Document escalation procedures
3. Create runbooks for common issues
4. Maintain on-call rotation (if team)
5. Post-incident reviews and documentation

---

## Development Timeline Estimate

### Phase 1: Foundation (Week 1-2)
- Environment setup
- Project structure
- Basic FastAPI app
- Basic Next.js app
- Azure OpenAI integration

### Phase 2: Backend Core (Week 3-5)
- Document processor
- Report simplifier with LangChain
- Symptom router with LangGraph
- API endpoints
- Testing

### Phase 3: ML Integration (Week 6-7)
- MobileNetV2 integration
- Grad-CAM implementation
- Image preprocessing
- GPT Vision fallback
- Testing

### Phase 4: Frontend (Week 8-10)
- UI components
- All three feature pages
- API integration
- Responsive design
- Error handling

### Phase 5: Integration & Testing (Week 11-12)
- End-to-end testing
- Bug fixes
- Performance optimization
- Security review

### Phase 6: Deployment (Week 13-14)
- Docker setup
- Azure deployment
- Monitoring setup
- Documentation
- Load testing

Total Estimated Time: 12-14 weeks for one engineer

---

## Quick Start Commands

### Backend
```bash
# Setup
cd tricare-backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Docker build
docker build -t tricare-backend .
docker run -p 8000:8000 --env-file .env tricare-backend
```

### Frontend
```bash
# Setup
cd tricare-frontend
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run production build
npm start
```

---

## Resources & Documentation

### Official Documentation
- Next.js: https://nextjs.org/docs
- FastAPI: https://fastapi.tiangolo.com
- LangChain: https://python.langchain.com
- LangGraph: https://langchain-ai.github.io/langgraph/
- Azure OpenAI: https://learn.microsoft.com/azure/ai-services/openai/
- PyTorch: https://pytorch.org/docs

### Useful Libraries
- react-dropzone: https://react-dropzone.js.org
- shadcn/ui: https://ui.shadcn.com
- PyDantic: https://docs.pydantic.dev
- Grad-CAM: https://github.com/jacobgil/pytorch-grad-cam

### Medical Datasets (for ML)
- ChestX-ray14: https://nihcc.app.box.com/v/ChestXray-NIHCC
- CheXpert: https://stanfordmlgroup.github.io/competitions/chexpert/
- MIMIC-CXR: https://physionet.org/content/mimic-cxr/

---

## Support & Next Steps

### Getting Started
1. Set up development environment following Phase 1
2. Start with backend foundation (FastAPI + basic endpoints)
3. Build one feature at a time (recommend: Report Simplifier first)
4. Test thoroughly before moving to next feature
5. Integrate frontend incrementally

### Best Practices
- Commit frequently with clear messages
- Write tests as you develop
- Document complex logic
- Use type hints in Python
- Keep components small and focused
- Follow principle of least privilege for secrets

### When You Need Help
- Azure OpenAI: Check Azure docs and support
- LangChain/LangGraph: Community Discord and GitHub issues
- Medical ML: Healthcare ML forums and papers
- General development: Stack Overflow, GitHub Discussions

---

## Appendix: Key Design Decisions

### Why LangGraph over Simple LangChain?
LangGraph provides state management for multi-step reasoning, perfect for the symptom router's sequential decision-making process.

### Why Separate Backend?
Python ML model (MobileNetV2) requires Python runtime. Keeping all AI logic together simplifies maintenance.

### Why MobileNetV2?
Lightweight, fast inference, good accuracy, suitable for edge deployment if needed later.

### Why Structured Outputs?
Medical applications require consistent, parseable responses for reliable UX. JSON mode ensures this.

### Why Azure Container Apps?
Serverless containers with auto-scaling, easier than AKS, cheaper than full VMs, integrated with Azure ecosystem.

---

**End of Documentation**

This guide provides the complete roadmap for developing TriCare AI. Follow each phase systematically, test thoroughly, and prioritize user safety and data security throughout development.