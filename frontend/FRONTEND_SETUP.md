# English Transfer Assistant - Frontend Setup

## Overview

This document provides a complete overview of the frontend configuration and module skeleton code created for the English Transfer Assistant project.

## Project Structure

```
frontend/
├── src/
│   ├── api/                    # API client modules
│   │   ├── index.ts           # Axios instance with interceptors
│   │   ├── auth.ts            # Authentication API
│   │   ├── analysis.ts        # Text analysis API
│   │   ├── history.ts         # History management API
│   │   ├── statistics.ts      # Statistics API
│   │   ├── export.ts          # Export functionality API
│   │   └── settings.ts        # User settings API
│   │
│   ├── assets/
│   │   └── styles/
│   │       └── main.css       # Tailwind CSS imports + custom styles
│   │
│   ├── components/
│   │   ├── auth/              # Authentication components
│   │   │   ├── LoginForm.vue
│   │   │   └── RegisterForm.vue
│   │   │
│   │   ├── common/            # Common reusable components
│   │   │   ├── Toast.vue
│   │   │   ├── LoadingSpinner.vue
│   │   │   └── ErrorDisplay.vue
│   │   │
│   │   ├── errors/            # Error display components
│   │   │   ├── ErrorCard.vue
│   │   │   └── ErrorHighlight.vue
│   │   │
│   │   ├── layout/            # Layout components
│   │   │   ├── Navbar.vue
│   │   │   ├── MainLayout.vue
│   │   │   └── LayoutControls.vue
│   │   │
│   │   └── panels/            # Main panel components
│   │       ├── InputPanel.vue
│   │       ├── ComparePanel.vue
│   │       └── AnalysisPanel.vue
│   │
│   ├── composables/           # Vue composables (business logic)
│   │   ├── useAuth.ts
│   │   ├── useAnalysis.ts
│   │   ├── useHistory.ts
│   │   └── useUI.ts
│   │
│   ├── router/
│   │   └── index.ts           # Vue Router configuration
│   │
│   ├── stores/                # Pinia state management
│   │   ├── types.ts           # TypeScript type definitions
│   │   ├── authStore.ts       # Authentication state
│   │   ├── analysisStore.ts   # Analysis state
│   │   ├── historyStore.ts    # History state
│   │   ├── uiStore.ts         # UI state
│   │   └── index.ts           # Store exports
│   │
│   ├── types/
│   │   └── index.ts           # Global TypeScript definitions
│   │
│   ├── utils/
│   │   ├── api.ts             # API utilities
│   │   ├── formatters.ts      # Date/token formatters
│   │   ├── validators.ts      # Input validators
│   │   └── constants.ts       # App constants
│   │
│   ├── views/                 # Page components
│   │   ├── Home.vue           # Main analysis interface
│   │   ├── Auth.vue           # Login/Register page
│   │   ├── History.vue        # History page
│   │   ├── Statistics.vue     # Statistics page
│   │   └── Settings.vue       # Settings page
│   │
│   ├── App.vue                # Root component
│   └── main.ts                # Application entry point
│
├── index.html                 # HTML entry point
├── package.json               # Dependencies
├── tailwind.config.js         # Tailwind configuration
├── tsconfig.json              # TypeScript configuration
├── tsconfig.app.json          # App TypeScript configuration
├── tsconfig.node.json         # Node TypeScript configuration
└── vite.config.ts             # Vite configuration
```

## Configuration Files

### 1. tailwind.config.js

- **Content paths**: Scans `./index.html` and `./src/**/*.{vue,js,ts,jsx,tsx}`
- **Dark mode**: Class-based (`'class'`)
- **Theme extensions**: Custom primary color palette (blue-based: #3b82f6)

### 2. vite.config.ts

- **Path aliases**: `@/*` → `./src/*`
- **API proxy**: `/api` → `http://localhost:8000`
- **Build optimizations**:
  - Manual chunks for vue-vendor and ui-vendor
  - ESBuild minification
  - Target: ESNext

### 3. tsconfig.app.json

- **Strict mode**: Enabled
- **Path aliases**: Matches Vite config (`@/*` → `./src/*`)
- **Linting options**:
  - `noUnusedLocals`: true
  - `noUnusedParameters`: true
  - `noFallthroughCasesInSwitch`: true

## Module Details

### State Management (Pinia Stores)

#### types.ts
- `AuthState`: User authentication state
- `AnalysisState`: Text analysis state (mode, view mode, progress)
- `HistoryState`: Analysis history with pagination
- `UIState`: UI state (panels, toasts, theme)

#### authStore.ts
- Login, register, logout actions
- JWT token management
- Auto token refresh on 401
- User profile fetching

#### analysisStore.ts
- Text analysis with progress tracking
- Correction mode switching (accuracy/naturalness)
- View mode switching (side-by-side, original-only, corrected-only)
- Error handling

#### historyStore.ts
- Paginated history fetching
- Filter support (mode, date range, search)
- Delete history items
- Pagination helpers

#### uiStore.ts
- Panel toggle management
- Dark mode with localStorage persistence
- Toast notifications with auto-dismiss
- Sidebar state

### API Clients

All API clients use a configured Axios instance with:
- Request interceptor: Adds auth token
- Response interceptor: Auto token refresh on 401
- Error handling helpers

#### API Endpoints
- `auth.ts`: POST /auth/login, /auth/register, /auth/refresh, GET /auth/me
- `analysis.ts`: POST /analyze
- `history.ts`: GET /history, GET /history/:id, DELETE /history/:id
- `statistics.ts`: GET /statistics/overview, /statistics/tokens
- `export.ts`: POST /export
- `settings.ts`: GET /settings, PUT /settings

### Components

#### Layout Components
- **Navbar.vue**: Navigation with logo, menu items, dark mode toggle, user menu
- **MainLayout.vue**: Three-panel grid layout (Input, Compare, Analysis)
- **LayoutControls.vue**: Panel visibility toggles

#### Panel Components
- **InputPanel.vue**: Text input, correction mode selection, analyze button
- **ComparePanel.vue**: Side-by-side original vs corrected text with view modes
- **AnalysisPanel.vue**: Error cards list with learning tips

#### Error Components
- **ErrorCard.vue**: Expandable error card with severity, type, suggestion
- **ErrorHighlight.vue**: Inline error highlighting (placeholder)

#### Common Components
- **Toast.vue**: Auto-dismissing notification with 4 types (success, error, warning, info)
- **LoadingSpinner.vue**: Animated spinner with size variants
- **ErrorDisplay.vue**: Styled error message display

#### Auth Components
- **LoginForm.vue**: Email/password login with validation
- **RegisterForm.vue**: Registration with username, email, password, confirm password

### Composables

Business logic wrappers around stores:

- **useAuth()**: Authentication helpers (login, logout, permissions)
- **useAnalysis()**: Analysis helpers (analyzeText, mode switching)
- **useHistory()**: History management (fetch, paginate, delete)
- **useUI()**: UI helpers (toasts, panels, dark mode)

### Views

Page-level components:
- **Home.vue**: Main analysis interface with navbar and panels
- **Auth.vue**: Login/register tabbed interface
- **History.vue**: History list with filters and pagination
- **Statistics.vue**: Error statistics and trends
- **Settings.vue**: User preferences

### Router

Routes with authentication guards:
- `/` - Home (public)
- `/auth` - Login/Register (public)
- `/history` - History (requires auth)
- `/statistics` - Statistics (requires auth)
- `/settings` - Settings (requires auth)

Navigation guards:
- Auto-redirect to login if not authenticated
- Auto-redirect to home if already authenticated on auth page
- Page title updates

### Utilities

#### api.ts
- Error message extraction
- Network/server/client error detection
- Rate limit detection

#### formatters.ts
- Date formatting (relative, absolute, short)
- Token count formatting (1K, 1M)
- Percentage calculation

#### validators.ts
- Email validation
- Password validation (8+ chars, letter + number)
- Username validation (3-20 chars, alphanumeric + underscore)
- Text length validation
- Chinese character detection
- English text detection

#### constants.ts
- Error types (grammar, tense, word_choice, etc.)
- Severity levels with colors
- Correction modes
- View modes
- User tiers (free, paid)
- Rate limits
- Pagination defaults
- HTTP status codes

## Key Features

### 1. Complete Type Safety
- All components use `<script setup lang="ts">`
- Comprehensive type definitions in `stores/types.ts`
- Global types in `types/index.ts`

### 2. Modular Architecture
- Separation of concerns: API → Store → Composable → Component
- Reusable components with clear props
- Composables for business logic

### 3. State Management
- Centralized state with Pinia
- Reactive computed properties
- Action-based state updates

### 4. Authentication Flow
- JWT-based authentication
- Auto token refresh on 401
- Route guards for protected pages

### 5. UI Features
- Dark mode support
- Toast notifications
- Panel collapse/expand
- Responsive layout
- Loading states

### 6. Error Handling
- Form validation with error messages
- API error interception
- User-friendly error displays

## Development Commands

```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run build  # Includes vue-tsc
```

## Next Steps

### TODO Items (marked in code)

All files contain `// TODO:` comments for actual implementation:

1. **Authentication**
   - Complete token refresh logic
   - Add redirect after login
   - Implement logout cleanup

2. **Analysis**
   - Add real-time progress updates
   - Implement streaming results
   - Add error highlighting in text

3. **History**
   - Implement filters UI
   - Add search functionality
   - Implement pagination UI

4. **Statistics**
   - Add charts (Chart.js or ECharts)
   - Implement trend visualization
   - Add token usage display

5. **UI**
   - Add proper icons (Heroicons)
   - Implement animations
   - Add responsive mobile menu
   - Implement sidebar

6. **Components**
   - Complete ErrorHighlight inline highlighting
   - Add export functionality UI
   - Implement settings form

7. **Testing**
   - Add unit tests (Vitest)
   - Add component tests
   - Add E2E tests (Playwright)

## Dependencies

### Core
- `vue@^3.5.24` - Framework
- `vue-router@^4.6.4` - Routing
- `pinia@^3.0.4` - State management
- `axios@^1.13.2` - HTTP client

### UI
- `tailwindcss@^3.4.19` - Styling
- `@headlessui/vue@^1.7.23` - UI components
- `@heroicons/vue@^2.2.0` - Icons

### Utilities
- `date-fns@^4.1.0` - Date formatting
- `clsx@^2.1.1` - Conditional classes
- `tailwind-merge@^3.4.0` - Tailwind class merging

### Dev
- `vite@^7.2.4` - Build tool
- `typescript@~5.9.3` - Type checking
- `vue-tsc@^3.1.4` - Vue type checking
- `vitest@^4.0.17` - Testing
- `@vitejs/plugin-vue@^6.0.1` - Vue plugin

## Notes

- All components follow Vue 3 Composition API best practices
- TypeScript strict mode enabled for better type safety
- Tailwind CSS configured for utility-first styling
- Dark mode support via class strategy
- API proxy configured for development (port 8000)
- Modular structure allows easy feature additions
- All code includes TODO comments for actual implementation
