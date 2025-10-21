# TriCare AI - Frontend

Next.js frontend for the TriCare AI medical triage and education platform.

## Features

- **Elegant Medical UI**: Modern, responsive design with Tailwind CSS
- **Medical Report Simplifier**: Upload and simplify medical reports
- **Symptom Router**: Interactive symptom analysis and specialist routing
- **X-ray Pre-Screen**: Image upload and analysis with heatmap visualization
- **Real-time Processing**: Loading states and error handling
- **Type-Safe**: Full TypeScript implementation

## Tech Stack

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom components with Lucide icons
- **Forms**: react-hook-form + zod validation
- **HTTP Client**: Axios
- **File Upload**: react-dropzone

## Prerequisites

- Node.js 18+ 
- npm or pnpm
- TriCare AI Backend running (default: http://localhost:8000)

## Installation

### 1. Install Dependencies

```bash
npm install
# or
pnpm install
```

### 2. Configure Environment Variables

Create `.env.local` from the example:

```bash
cp .env.local.example .env.local
```

Required environment variables:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Running the Application

### Development Mode

```bash
npm run dev
# or
pnpm dev
```

The application will be available at:
- **Frontend**: http://localhost:3000

### Production Build

```bash
npm run build
npm run start
```

### Type Checking

```bash
npm run type-check
```

### Linting

```bash
npm run lint
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # Root layout with Header/Footer
│   │   ├── page.tsx            # Landing page
│   │   ├── reports/            # Report simplifier pages
│   │   ├── symptoms/           # Symptom router pages
│   │   └── imaging/            # Imaging pre-screen pages
│   ├── components/
│   │   ├── shared/             # Reusable components
│   │   ├── reports/            # Report feature components
│   │   ├── symptoms/           # Symptom feature components
│   │   └── imaging/            # Imaging feature components
│   ├── lib/
│   │   ├── api-client.ts       # API wrapper functions
│   │   ├── utils.ts            # Utility functions
│   │   └── constants.ts        # App constants
│   ├── types/                  # TypeScript type definitions
│   └── hooks/                  # Custom React hooks
├── public/                     # Static assets
├── tailwind.config.ts          # Tailwind configuration
├── next.config.js              # Next.js configuration
└── README.md                   # This file
```

## Key Pages

### Landing Page (`/`)
- Feature overview
- Navigation to all tools
- Medical disclaimer

### Medical Report Simplifier (`/reports`)
- File upload (PDF, images)
- Text input option
- Plain-language summary display
- Key findings with severity indicators
- Specialist recommendations

### Symptom Router (`/symptoms`)
- Symptom description form
- Patient metadata (age, sex, etc.)
- Urgency level display
- Specialist recommendation
- Red flags and preparation tips

### X-ray Pre-Screen (`/imaging`)
- Medical image upload
- Image type selection
- Prediction display (normal/abnormal)
- Heatmap overlay visualization
- Detailed explanation

## Design System

### Colors

- **Medical Blue**: Primary brand color for medical/clinical elements
- **Health Green**: Success states and positive indicators
- **Urgent Red**: Warnings, errors, and emergency indicators
- **Neutral Gray**: Background and text elements

### Components

All components follow a consistent design pattern:
- **Cards**: Elevated surfaces with shadow and border
- **Buttons**: Clear call-to-action styling
- **Forms**: Accessible inputs with proper validation feedback
- **Badges**: Contextual information indicators

## API Integration

The frontend communicates with the backend via the API client (`lib/api-client.ts`):

```typescript
import { simplifyReport, routeSymptoms, prescreenImage } from '@/lib/api-client';

// Example: Simplify a report
const result = await simplifyReport(file, text);

// Example: Route symptoms
const recommendation = await routeSymptoms({
  symptoms: "persistent cough",
  age: 35,
  // ...
});

// Example: Pre-screen imaging
const analysis = await prescreenImage(file, "x-ray", "chest");
```

## Error Handling

All API calls include comprehensive error handling:
- Network errors
- Validation errors (422)
- Server errors (500)
- Timeout errors

Errors are displayed to users with helpful messages and retry options.

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project in Vercel
3. Set environment variables
4. Deploy

```bash
vercel --prod
```

### Docker

```bash
docker build -t tricare-frontend .
docker run -p 3000:3000 tricare-frontend
```

### Static Export

For static hosting:

```bash
npm run build
# Deploy the 'out' directory
```

## Important Disclaimers

⚠️ **CRITICAL**: This application is for EDUCATIONAL PURPOSES ONLY.

- NOT a medical device
- NOT for diagnostic use
- NOT a replacement for professional medical advice
- Always consult licensed healthcare providers

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Accessibility

- Semantic HTML structure
- ARIA labels for interactive elements
- Keyboard navigation support
- Screen reader friendly

## Performance

- Server-side rendering for fast initial load
- Image optimization with next/image
- Code splitting and lazy loading
- Optimized bundle size

## Security

- Environment variables for sensitive data
- HTTPS in production
- Input validation and sanitization
- XSS protection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues or questions:
- Create an issue on GitHub
- Email: support@tricare-ai.com

## License

MIT License - See LICENSE file for details

---

Built with ❤️ for medical education
