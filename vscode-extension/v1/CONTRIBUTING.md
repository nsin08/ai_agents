# Contributing Guide

**Thank you for your interest in contributing to the AI Agent VSCode Extension!**

This document explains how to contribute code, report bugs, suggest features, and help improve the project.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Testing](#testing)
6. [Submitting Pull Requests](#submitting-pull-requests)
7. [Reporting Issues](#reporting-issues)
8. [Code Standards](#code-standards)
9. [Commit Guidelines](#commit-guidelines)

---

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

- **Respect others:** Different backgrounds and experience levels
- **Be constructive:** Provide helpful feedback
- **Report concerns:** Contact maintainers privately if issues arise
- **Collaborate:** Work together toward improvements

---

## Getting Started

### 1. Fork the Repository

```bash
# Go to: https://github.com/nsin08/ai_agents
# Click "Fork" button
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ai_agents.git
cd ai_agents
```

### 2. Create a Feature Branch

```bash
# Update develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name
# OR for bug fixes
git checkout -b fix/issue-number-description
```

### 3. Set Up Development Environment

```bash
cd vscode-extension/v1
npm install
npm run compile
```

---

## Development Setup

### Quick Start

```bash
# Navigate to extension
cd vscode-extension/v1

# Install dependencies
npm install

# Start development mode (watch + compile)
npm run watch
```

### Launch Extension

```bash
# Press F5 in VSCode to launch Extension Development Host
# OR use command:
code --extensionDevelopmentPath=. .
```

### Available Commands

```bash
npm run compile          # Compile TypeScript
npm run watch          # Watch mode (auto-compile)
npm test               # Run all tests
npm test -- -t "name"  # Run specific test
npm run lint           # Check code quality
npm run lint -- --fix  # Auto-fix lint issues
npm run format         # Format code
npm run clean          # Clean build artifacts
```

---

## Making Changes

### Code Style

**TypeScript/JavaScript:**
```typescript
// Use const/let, not var
const myVar = 'value';

// Use arrow functions
const myFunc = (arg: string): string => {
  return arg.toUpperCase();
};

// Use async/await
const getData = async (): Promise<Data> => {
  const result = await fetchData();
  return result;
};

// Type everything (no 'any')
const add = (a: number, b: number): number => a + b;

// Document public methods
/**
 * Does something important
 * @param input - The input value
 * @returns The result
 */
public async doSomething(input: string): Promise<string> {
  // Implementation
}
```

### File Organization

- **Services:** Business logic in `src/services/`
- **Panels:** UI components in `src/panels/`
- **Models:** Type definitions in `src/models/`
- **Views:** HTML templates in `src/views/`
- **Tests:** Corresponding test in `tests/`

### Creating New Features

**Example: Add a new command**

1. **Create service if needed:**
   ```typescript
   // src/services/MyService.ts
   export class MyService {
     async doTask(): Promise<string> {
       return 'done';
     }
   }
   ```

2. **Add to package.json:**
   ```json
   "commands": [
     {
       "command": "ai-agent.myCommand",
       "title": "Agent: My Command"
     }
   ]
   ```

3. **Register in extension.ts:**
   ```typescript
   const myService = new MyService();
   context.subscriptions.push(
     vscode.commands.registerCommand('ai-agent.myCommand', async () => {
       const result = await myService.doTask();
       vscode.window.showInformationMessage(result);
     })
   );
   ```

4. **Add tests:**
   ```typescript
   // tests/unit/MyService.test.ts
   describe('MyService', () => {
     it('should do task', async () => {
       const service = new MyService();
       const result = await service.doTask();
       expect(result).toBe('done');
     });
   });
   ```

---

## Testing

### Write Tests

All changes should include tests.

```typescript
// tests/unit/MyService.test.ts
describe('MyService', () => {
  let service: MyService;

  beforeEach(() => {
    service = new MyService();
  });

  it('should return expected value', async () => {
    const result = await service.doTask();
    expect(result).toBe('expected');
  });

  it('should handle errors', async () => {
    expect(async () => {
      await service.failingTask();
    }).rejects.toThrow();
  });
});
```

### Run Tests

```bash
# All tests
npm test

# Specific file
npm test -- tests/unit/MyService.test.ts

# Watch mode
npm test -- --watch

# Coverage
npm test -- --coverage
```

### Expected Results

- ✅ All tests pass: 189/189
- ✅ New tests added for your changes
- ✅ Coverage maintained or improved (85%+)
- ✅ No type errors
- ✅ Lint checks pass

---

## Submitting Pull Requests

### Before Submitting

```bash
# 1. Update from develop
git fetch origin
git rebase origin/develop

# 2. Run tests
npm test

# 3. Check code quality
npm run lint
npm run compile -- --noEmit

# 4. Format code
npm run format

# 5. Commit
git commit -m "feat: Add my feature (fixes #123)"

# 6. Push to your fork
git push origin feature/your-feature-name
```

### Create PR on GitHub

1. **Go to:** https://github.com/nsin08/ai_agents/pulls
2. **Click:** "New Pull Request"
3. **Select:**
   - Base: `develop` (not main)
   - Compare: `your-fork:feature/your-feature`
4. **Fill in title and description:**
   ```markdown
   ## Description
   What does this PR do?

   ## Related Issue
   Fixes #123

   ## Type
   - [ ] Bug fix
   - [ ] Feature
   - [ ] Documentation
   - [ ] Refactoring

   ## Checklist
   - [ ] Tests pass (npm test)
   - [ ] Code quality (npm run lint)
   - [ ] Type check (npm run compile)
   - [ ] Documentation updated
   - [ ] No breaking changes

   ## Screenshots (if applicable)
   [Add screenshots]
   ```

5. **Submit PR**

### PR Requirements

- ✅ Title: Clear and descriptive
- ✅ Description: Explain what and why
- ✅ Tests: All passing, new tests included
- ✅ Code quality: No lint violations
- ✅ Types: No TypeScript errors
- ✅ Docs: Updated if needed
- ✅ Base branch: Always `develop`

### PR Review Process

1. **Automated checks:**
   - Tests run (189 tests)
   - Linting checks
   - Type checking
   - Coverage analysis

2. **Code review:**
   - Maintainers review code
   - Feedback provided
   - Changes requested if needed

3. **Approval & Merge:**
   - CODEOWNER approves
   - PR merged to develop
   - Your changes available in next release

---

## Reporting Issues

### Bug Report

**Go to:** https://github.com/nsin08/ai_agents/issues/new

**Include:**
```markdown
## Description
Brief description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Observe bug

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- VSCode version: (Help → About)
- Extension version: (Extensions panel)
- OS: Windows/macOS/Linux
- LLM Provider: Ollama/OpenAI/etc.

## Logs
Output from Developer Tools:
Help → Toggle Developer Tools → Console tab
(Paste error message)

## Screenshots
[If applicable]
```

### Feature Request

**Go to:** https://github.com/nsin08/ai_agents/issues/new

**Include:**
```markdown
## Feature Description
What should the extension do?

## Use Case
Why is this useful?

## Proposed Solution
How should it work?

## Alternatives
Other ways to solve this?

## Additional Context
Screenshots, examples, etc.
```

---

## Code Standards

### TypeScript

```typescript
// ✅ DO:
const getValue = (): string => 'value';
const addNumbers = (a: number, b: number): number => a + b;

// ❌ DON'T:
const getValue = function() { return 'value'; };
const addNumbers = (a: any, b: any) => a + b;
```

### Naming

```typescript
// Classes: PascalCase
class ChatPanel {}

// Functions/Variables: camelCase
const sendMessage = async () => {};

// Constants: UPPER_SNAKE_CASE
const MAX_RETRIES = 3;

// Interfaces: PascalCase, prefix with I
interface IMessageService {}
```

### Comments

```typescript
// Good: Explain WHY, not WHAT
// Retry mechanism handles temporary network failures
async function retryWithBackoff() {}

// Bad: Redundant comments
// Increment counter
counter++;

// Good: Document public APIs
/**
 * Send a message to the agent
 * @param message - The message text
 * @returns Promise resolving to agent response
 * @throws Error if connection fails
 */
public async sendMessage(message: string): Promise<string> {}
```

### Error Handling

```typescript
// ✅ Good error handling
try {
  await performAction();
} catch (error) {
  vscode.window.showErrorMessage(`Failed: ${error instanceof Error ? error.message : String(error)}`);
}

// ❌ Silent failures
async function doSomething() {
  try {
    await performAction();
  } catch (error) {
    // Swallowing error - bad!
  }
}
```

---

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Code style (no logic change)
- `refactor` - Refactoring
- `test` - Adding/updating tests
- `chore` - Build, dependencies

**Examples:**
```bash
git commit -m "feat(chat): Add conversation history search"
git commit -m "fix(agent): Handle connection timeouts"
git commit -m "docs: Update installation guide"
git commit -m "test: Add HistoryService tests"
git commit -m "refactor(services): Extract common logic"
```

**Commit messages:**
- Use imperative mood: "Add feature" not "Added feature"
- Keep subject under 50 characters
- Reference issues: "fixes #123"
- Detailed body: Explain why, not what

---

## Getting Help

### Questions

- **GitHub Discussions:** https://github.com/nsin08/ai_agents/discussions
- **Create Issue:** https://github.com/nsin08/ai_agents/issues

### Documentation

- **Setup:** [DEVELOPMENT.md](DEVELOPMENT.md)
- **Building:** [BUILD.md](BUILD.md)
- **Testing:** [TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md)
- **Overview:** [README.md](README.md)

---

## Recognition

Contributors are recognized in:
- Release notes
- GitHub contributors page
- Project documentation

Thank you for helping improve AI Agent VSCode Extension!

---

## 📚 Related Guides

- **[README.md](README.md)** ← Main documentation hub
- **[DEVELOPMENT.md](DEVELOPMENT.md)** ← Development setup, architecture, debugging
- **[BUILD.md](BUILD.md)** ← Building, testing, packaging, deployment
- **[TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md)** ← Testing strategies and coverage

---

**Back to:** [README.md](README.md)

