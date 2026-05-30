# Lumidoc

A production-ready AI-powered document and media chat platform built with React 18, Tailwind CSS, and modern web technologies.

## Features

- **Document Upload**: Support for PDF, MP3, MP4, WAV, MOV, M4A files
- **AI Chatbot**: Interactive conversations about uploaded content
- **AI Summaries**: Automatic document and media summarization
- **Media Timestamps**: Extract and navigate to specific topics in audio/video
- **Real-time Player**: Embedded audio/video playback with seek controls
- **Chat History**: Organized by date with rich preview cards
- **File Library**: Grid and list views with search and filtering
- **Responsive Design**: Desktop, tablet, and mobile optimized
- **Glassmorphism UI**: Modern aesthetic with soft shadows and blur effects

## Tech Stack

- React 18 (Functional Components + Hooks)
- React Router v6
- Tailwind CSS v3
- Zustand (State Management)
- TanStack Query v5 (React Query)
- Axios (HTTP Client)
- Framer Motion (Animations)
- React Dropzone (File Uploads)
- React Player (Media Playback)
- Lucide React (Icons)
- React Hot Toast (Notifications)
- date-fns (Date Formatting)
- Vite (Build Tool)

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Clone or extract the project
cd lumidoc

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
VITE_API_BASE_URL=http://localhost:3000/api
```

## Project Structure

```
lumidoc/
├── src/
│   ├── components/
│   │   ├── layout/          # Sidebar, MainLayout
│   │   ├── chat/            # ChatMessage, ChatInput, TypingIndicator, MediaPlayer
│   │   ├── upload/          # FileDropzone, UploadQueue
│   │   └── ui/              # Button, Input, Card, Skeleton, Avatar, Badge
│   ├── pages/               # LoginPage, DashboardPage, ChatPage, UploadPage, FilesPage, SettingsPage
│   ├── store/               # Zustand store with persistence
│   ├── types/               # TypeScript interfaces
│   ├── lib/                 # Utilities, API client
│   ├── App.tsx              # Router setup
│   ├── main.tsx             # Entry point
│   └── index.css            # Tailwind + custom styles
├── public/                  # Static assets
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
└── README.md
```

## Routes

| Route | Page | Description |
|-------|------|-------------|
| `/login` | LoginPage | Authentication with sign in/up |
| `/dashboard` | DashboardPage | Main dashboard with quick actions |
| `/chat/:id` | ChatPage | Active chat with AI |
| `/upload` | UploadPage | File upload with drag-and-drop |
| `/files` | FilesPage | File library management |
| `/settings` | SettingsPage | Profile, API keys, preferences |

## Design System

### Colors
- Primary: `#6C63FF` (Violet-purple)
- Secondary: `#A78BFA` (Lavender)
- Accent: `#10B981` (Teal-green)
- Background: `#F3F0FF` (Soft lavender-white)

### Typography
- Display: Plus Jakarta Sans
- Body: DM Sans
- Mono: JetBrains Mono

## License

MIT
