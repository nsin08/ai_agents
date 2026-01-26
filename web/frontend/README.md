# Frontend - React + TypeScript Chat Interface

**Learning Lab**: React 18 application demonstrating modern frontend patterns for AI agent interactions. This complements the backend API and serves as a reference implementation for building accessible, responsive chat interfaces.

---

## 🎯 Learning Objectives

This frontend lab teaches:

1. **React Hooks & State Management** — useState, useEffect, useRef for managing chat state
2. **TypeScript Integration** — Type-safe API contracts, strict mode configuration
3. **Component Architecture** — Modular components with clear responsibilities
4. **Accessibility (a11y)** — ARIA labels, keyboard navigation, semantic HTML (WCAG AA)
5. **Responsive Design** — Mobile-first CSS with breakpoints (320px, 768px, 1024px)
6. **Dark Mode** — Theme system with CSS variables and localStorage persistence
7. **API Integration** — REST client services with error handling

---

## 🏗️ Architecture

### Component Hierarchy

```
App.tsx (Root)
└── Chat.tsx (Main Interface, 394 lines)
    ├── ThemeToggle.tsx (Dark Mode, 31 lines)
    ├── DebugPanel.tsx (Metrics Display, 97 lines)
    ├── ConfigPanel.tsx (Settings, 232 lines)
    ├── ConversationExport.tsx (Export, 152 lines)
    └── SettingsDrawer.tsx (Provider Config, 180 lines)
```

### Service Layer

```
services/
├── chatService.ts           # HTTP client for /api/chat endpoints
├── providerService.ts       # HTTP client for /api/providers endpoints
└── configService.ts         # HTTP client for /api/config endpoints
```

### Type System

```
types/
├── providers.ts             # ProviderType, ProviderInfo, ChatRequest/Response
└── config.ts                # AgentConfig, DebugMetadata, ConfigPreset
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- npm 8+

### Setup (3 minutes)

```bash
cd web/frontend

# Install dependencies
npm install

# Start development server (http://localhost:3000)
npm start

# Build for production
npm run build

# Run tests (when implemented)
npm test
```

---

## 📁 Directory Structure

```
frontend/
├── package.json                    # Dependencies: React 18, TypeScript 5.9
├── tsconfig.json                   # TypeScript strict configuration
├── public/
│   ├── index.html                  # HTML entry point
│   ├── favicon.ico
│   └── manifest.json
└── src/
    ├── index.tsx                   # React root, render App
    ├── index.css                   # Global styles, CSS reset
    ├── App.tsx                     # Root component (150 lines)
    ├── App.css                     # Root styles, CSS variables for theming
    │
    ├── components/                 # React Components
    │   ├── Chat.tsx                # Main chat interface (394 lines)
    │   ├── Chat.css                # Chat layout, message styles
    │   ├── DebugPanel.tsx          # Performance metrics display (97 lines)
    │   ├── DebugPanel.css          # Debug panel styling
    │   ├── ConfigPanel.tsx         # Configuration controls (232 lines)
    │   ├── ConfigPanel.css         # Config UI styling
    │   ├── ConversationExport.tsx  # Export JSON/Markdown (152 lines)
    │   ├── ConversationExport.css  # Export modal styling
    │   ├── ThemeToggle.tsx         # Dark mode toggle (31 lines)
    │   ├── ThemeToggle.css         # Theme toggle button
    │   ├── SettingsDrawer.tsx      # Provider settings (180 lines)
    │   └── SettingsDrawer.css      # Settings drawer layout
    │
    ├── services/                   # API Client Services
    │   ├── chatService.ts          # Chat API (120 lines)
    │   ├── providerService.ts      # Provider API (80 lines)
    │   └── configService.ts        # Config API (90 lines)
    │
    └── types/                      # TypeScript Type Definitions
        ├── providers.ts            # Provider-related types (40 lines)
        └── config.ts               # Config-related types (60 lines)
```

---

## 🎓 Key Components (Learning Guide)

### 1. Chat.tsx (Main Interface)

**Purpose**: Primary chat UI with message history, input, and integrations

**Key Concepts**:
- **useState** for messages, loading, session management
- **useEffect** for initialization, model loading, keyboard shortcuts
- **useRef** for scrolling to latest message
- **Conditional Rendering** for debug/config panels

**Code Structure** (394 lines):
```typescript
// State Management (lines 33-60)
const [messages, setMessages] = useState<Message[]>([]);
const [sessionId, setSessionId] = useState<string>("");
const [showDebugPanel, setShowDebugPanel] = useState(false);
// ... 15 more state variables

// Effects (lines 62-100)
useEffect(() => {
  initializeSession();
  loadProviders();
}, []);

useEffect(() => {
  // Load models when provider changes
}, [config.provider]);

useEffect(() => {
  // Keyboard shortcuts (Escape, etc.)
}, [showSettings, showDebugPanel, showConfigPanel]);

// Event Handlers (lines 150-220)
const handleSendMessage = async () => { ... };
const handleProviderChange = (provider: ProviderType) => { ... };

// Render (lines 240-390)
return (
  <div className="app">
    <header>...</header>
    <div className="chat-container">...</div>
    <div className="input-area">...</div>
    {showDebugPanel && <DebugPanel ... />}
    {showConfigPanel && <ConfigPanel ... />}
  </div>
);
```

**Exercise**: Add a "Clear Chat" button that resets the session and messages

---

### 2. DebugPanel.tsx (Performance Metrics)

**Purpose**: Display 14 debug metrics when debug mode enabled

**Key Concepts**:
- **Props interface** for type-safe component API
- **Conditional rendering** based on debug data
- **Copy to clipboard** functionality
- **Collapsible sections** for better UX

**Props**:
```typescript
interface DebugPanelProps {
  metadata: DebugMetadata | null;
  isVisible: boolean;
  onClose: () => void;
}
```

**14 Metrics Displayed**:
1. Input Tokens
2. Output Tokens
3. Total Tokens
4. Latency (ms)
5. Provider
6. Model
7. Agent State
8. Tool Calls Count
9. Reasoning Steps
10. Error Details
11. Session Config
12. Timestamp
13. Request ID
14. Cost Estimate

**Exercise**: Add a chart showing token usage over time (use Chart.js or Recharts)

---

### 3. ConfigPanel.tsx (Configuration Controls)

**Purpose**: Allow users to customize agent behavior with presets and sliders

**Key Concepts**:
- **Controlled inputs** (value + onChange pattern)
- **Range sliders** with min/max/step
- **Preset buttons** for quick configuration
- **Form validation** on frontend

**Controls**:
```typescript
// Max Turns Slider (1-10)
<input 
  type="range" 
  min={1} 
  max={10} 
  value={config.max_turns}
  onChange={handleMaxTurnsChange}
/>

// Temperature Slider (0.0-2.0)
<input 
  type="range" 
  min={0} 
  max={2} 
  step={0.1}
  value={config.temperature}
/>

// System Prompt (optional textarea)
<textarea 
  value={config.system_prompt || ""}
  onChange={handleSystemPromptChange}
/>

// Presets
<button onClick={() => applyPreset("creative")}>Creative</button>
<button onClick={() => applyPreset("precise")}>Precise</button>
<button onClick={() => applyPreset("balanced")}>Balanced</button>
```

**Exercise**: Add a "Save Custom Preset" feature that stores user's config in localStorage

---

### 4. ConversationExport.tsx (Export Functionality)

**Purpose**: Export conversation history as JSON or Markdown

**Key Concepts**:
- **Data transformation** (messages → export format)
- **File download** (createObjectURL + anchor tag)
- **Clipboard API** (navigator.clipboard.writeText)
- **LocalStorage** for saved conversations

**Export Formats**:

**JSON**:
```json
{
  "exported_at": "2026-01-26T14:30:00Z",
  "session_id": "abc-123",
  "total_turns": 5,
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2026-01-26T14:25:00Z"
    },
    ...
  ]
}
```

**Markdown**:
```markdown
# Conversation Export
**Exported**: 2026-01-26T14:30:00Z
**Session ID**: abc-123
**Total Turns**: 5

## User
Hello

## Assistant
Hi! How can I help you today?
```

**Exercise**: Add PDF export using jsPDF library

---

### 5. ThemeToggle.tsx (Dark Mode)

**Purpose**: Toggle between light and dark themes

**Key Concepts**:
- **CSS variables** for theming (`--bg-primary`, `--text-primary`)
- **LocalStorage** persistence (`localStorage.setItem/getItem`)
- **useEffect** to load saved theme on mount
- **Document class** manipulation

**Implementation**:
```typescript
const [isDark, setIsDark] = useState(false);

useEffect(() => {
  // Load saved theme
  const saved = localStorage.getItem("theme");
  if (saved === "dark") {
    setIsDark(true);
    document.documentElement.classList.add("dark");
  }
}, []);

const toggleTheme = () => {
  setIsDark(!isDark);
  document.documentElement.classList.toggle("dark");
  localStorage.setItem("theme", isDark ? "light" : "dark");
};
```

**CSS Variables** (App.css):
```css
:root {
  --bg-primary: #ffffff;
  --text-primary: #000000;
  --border-color: #e0e0e0;
}

.dark {
  --bg-primary: #1e1e1e;
  --text-primary: #ffffff;
  --border-color: #404040;
}
```

**Exercise**: Add a smooth theme transition animation (0.3s)

---

### 6. SettingsDrawer.tsx (Provider Configuration)

**Purpose**: Select provider, model, and configure API keys

**Key Concepts**:
- **Drawer/Modal pattern** (slide-in from right)
- **Dynamic dropdowns** (provider → models)
- **API key masking** (display as ****)
- **Form state management**

**Provider Flow**:
1. User selects provider from dropdown
2. Frontend loads models: `GET /api/providers/{provider_id}/models`
3. User selects model from dynamic list
4. If paid provider (OpenAI, etc.), prompt for API key
5. User saves configuration
6. Frontend updates `ProviderConfig` state

**Exercise**: Add connection status indicator (ping provider API to check availability)

---

## 🎨 Styling Approach

### CSS Variables (Theme System)

```css
/* Light Theme (default) */
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --text-primary: #000000;
  --text-secondary: #666666;
  --border-color: #e0e0e0;
  --accent-color: #007bff;
  --error-color: #dc3545;
  --success-color: #28a745;
}

/* Dark Theme */
.dark {
  --bg-primary: #1e1e1e;
  --bg-secondary: #2a2a2a;
  --text-primary: #ffffff;
  --text-secondary: #b0b0b0;
  --border-color: #404040;
  --accent-color: #4da3ff;
  --error-color: #ff6b6b;
  --success-color: #51cf66;
}
```

### Responsive Breakpoints

```css
/* Mobile (default, 320px+) */
.chat-container {
  flex-direction: column;
  padding: 10px;
}

/* Tablet (768px+) */
@media (min-width: 768px) {
  .chat-container {
    padding: 20px;
  }
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
  .chat-container {
    max-width: 1200px;
    margin: 0 auto;
  }
}
```

### Accessibility (WCAG AA Compliance)

```css
/* Focus Indicators */
button:focus,
input:focus,
textarea:focus {
  outline: 2px solid var(--accent-color);
  outline-offset: 2px;
}

/* High Contrast Text */
.text-primary {
  color: var(--text-primary);
  /* Ensures 4.5:1 contrast ratio */
}

/* Touch Targets (minimum 44x44px) */
button {
  min-width: 44px;
  min-height: 44px;
}
```

---

## 🧪 Testing Strategy (Future)

### Unit Tests (React Testing Library)

```typescript
// Chat.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import Chat from './Chat';

test('renders chat interface', () => {
  render(<Chat />);
  expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
});

test('sends message when Enter pressed', () => {
  render(<Chat />);
  const input = screen.getByRole('textbox');
  fireEvent.change(input, { target: { value: 'Hello' } });
  fireEvent.keyDown(input, { key: 'Enter' });
  // Assert message sent
});
```

### Integration Tests (Cypress/Playwright)

```typescript
// e2e/chat.spec.ts
describe('Chat Flow', () => {
  it('should send message and receive response', () => {
    cy.visit('http://localhost:3000');
    cy.get('[data-testid="message-input"]').type('Hello');
    cy.get('[data-testid="send-button"]').click();
    cy.contains('Hello').should('be.visible');
    cy.contains('Mock response').should('be.visible');
  });
});
```

---

## 🔐 Security Considerations

1. **API Key Storage**: Never store API keys in localStorage (use session memory only)
2. **XSS Prevention**: React escapes content by default, but avoid `dangerouslySetInnerHTML`
3. **CORS**: Backend configured to allow only known origins
4. **Input Validation**: Frontend validates before sending to API
5. **HTTPS Only**: Production deployment enforces SSL

---

## 🚀 Build & Deployment

### Development Build
```bash
npm start
# Starts webpack dev server at http://localhost:3000
# Hot reload enabled
# Source maps included
```

### Production Build
```bash
npm run build
# Creates optimized build/ directory
# Minified and bundled
# Ready for static hosting (nginx, S3, Vercel, etc.)
```

### Deployment Options

**1. Nginx (Recommended)**:
```nginx
server {
  listen 80;
  root /var/www/html;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;
  }

  location /api/ {
    proxy_pass http://localhost:8000/api/;
  }
}
```

**2. Vercel**:
```bash
npm install -g vercel
vercel --prod
```

**3. AWS S3 + CloudFront**:
```bash
aws s3 sync build/ s3://your-bucket/
aws cloudfront create-invalidation --distribution-id E123 --paths "/*"
```

---

## 📦 Dependencies

### Production Dependencies

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-scripts": "5.0.1",
  "typescript": "^5.9.3"
}
```

### Development Dependencies

```json
{
  "@testing-library/react": "^13.0.0",
  "@testing-library/jest-dom": "^5.16.5",
  "@types/react": "^18.0.0",
  "@types/react-dom": "^18.0.0"
}
```

**Total bundle size** (production): ~150KB gzipped

---

## 🎓 Learning Exercises

### Exercise 1: Message Reactions
Add emoji reactions to messages (like Slack)
- UI: Heart, thumbs up, laugh emoji buttons below each message
- State: Track reactions per message in `Message` interface
- Persistence: Store in backend (new endpoint: `POST /api/messages/{id}/reactions`)

### Exercise 2: Typing Indicator
Show "Assistant is typing..." when waiting for response
- Use loading state to show animated ellipsis
- CSS animation: `@keyframes typing { ... }`
- Clear when response received

### Exercise 3: Message Search
Add search bar to filter messages by content
- UI: Search input in header
- Logic: Filter `messages` array with `includes()` or regex
- Highlight: Wrap matching text in `<mark>` tags

### Exercise 4: Voice Input
Add speech-to-text for message input
- API: Web Speech API (`webkitSpeechRecognition`)
- UI: Microphone button next to send
- Accessibility: Provide visual feedback during recording

### Exercise 5: Conversation History
Show list of past conversations in sidebar
- UI: Collapsible left sidebar with conversation list
- Data: Fetch from `GET /api/chat/sessions`
- Click to load: Fetch messages for selected session

---

## 🔗 Related Resources

**Official Docs**:
- [React Docs](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [React Testing Library](https://testing-library.com/react)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

**Backend Integration**:
- See `../backend/README.md` for API documentation
- See `../ARCHITECTURE.md` for full system design

---

## 🤝 Contributing

When adding new components:
1. Create component file (e.g., `NewFeature.tsx`)
2. Create corresponding CSS file (e.g., `NewFeature.css`)
3. Add TypeScript interfaces for props
4. Implement accessibility (ARIA labels, keyboard nav)
5. Test on mobile, tablet, desktop
6. Add dark mode support using CSS variables

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-26  
**Tech Stack**: React 18 + TypeScript 5.9  
**Status**: ✅ Production Ready
