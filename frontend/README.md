# DSir Frontend

Next.js 15 application for the DSir programming education platform.

## Tech Stack
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **State**: React Query + Zustand
- **UI**: Custom design system, Lucide icons
- **Animations**: Framer Motion

## Quick Start

```bash
# Install dependencies
npm install

# Copy environment
cp .env.local.example .

# Development server
npm run dev

# Build for production
npm run build
npm start
```

## Project Structure
```
src/
├── app/              # App Router pages
│   ├── login/        # Login page
│   ├── signup/       # Registration page
│   ├── dashboard/    # User dashboard
│   ├── courses/      # Course browse, detail, learning
│   ├── practice/     # Practice exercises hub
│   ├── revision/     # Spaced repetition flashcards
│   ├── ai/           # AI assistant chat
│   ├── profile/      # User profile
│   └── settings/     # Account settings
├── components/
│   ├── ui/           # Design system primitives
│   └── layout/       # App shell, sidebar, header
├── lib/
│   ├── api.ts        # API client
│   ├── auth.tsx       # Auth context & provider
│   ├── types.ts      # TypeScript types
│   └── utils.ts      # Utility functions
└── hooks/            # Custom React hooks
```

## Environment Variables
`NEXT_PUBLIC_API_URL` — Backend API base URL (default: http://localhost:8000)
