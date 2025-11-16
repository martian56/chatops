# ChatOps Web Frontend

React + TypeScript frontend for the ChatOps server monitoring platform.

## Features

- **Real-time Dashboard**: Live metrics, logs, and system status
- **Docker Management**: Control containers from the web interface
- **Alert Management**: Configure and monitor alert thresholds
- **Terminal Access**: Execute commands remotely via web terminal
- **Modern UI**: Dark-themed interface built with Tailwind CSS and Shadcn UI

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **TanStack Query** - Data fetching and caching
- **React Router** - Client-side routing
- **Zustand** - State management
- **Tailwind CSS** - Styling
- **Shadcn UI** - Component library
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **WebSockets** - Real-time communication

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your API URL
```

### Development

```bash
# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
src/
├── api/          # API client functions
├── components/   # React components
│   ├── charts/   # Data visualization components
│   ├── forms/    # Form components
│   ├── layout/   # Layout components
│   └── ui/       # Shadcn UI components
├── hooks/        # Custom React hooks
├── pages/        # Page components
├── store/        # Zustand stores
└── utils/        # Utility functions and types
```

## Development

### Adding New Components

Components are organized by feature:
- `components/charts/` - Data visualization
- `components/forms/` - Form components
- `components/layout/` - Layout and navigation
- `components/ui/` - Reusable UI components

### State Management

- **Zustand** for global state (auth, servers)
- **TanStack Query** for server state and caching
- **Local state** with React hooks for component-specific state

### API Integration

All API calls are centralized in `src/api/`:
- Each resource has its own file (e.g., `servers.ts`, `alerts.ts`)
- Uses Axios instance from `utils/fetcher.ts`
- Automatic token refresh on 401 errors

## Building for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

## License

MIT License - see LICENSE file for details
