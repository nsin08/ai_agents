// Mock implementation of vscode module for testing

export const workspace = {
  getConfiguration: jest.fn().mockReturnValue({
    get: jest.fn((key: string) => {
      const defaults: Record<string, any> = {
        'aiAgent.provider': 'mock',
        'aiAgent.model': 'llama2',
        'aiAgent.baseUrl': 'http://localhost:11434',
        'aiAgent.apiKey': '',
        'aiAgent.maxTurns': 5,
        'aiAgent.timeout': 30
      };
      return defaults[`aiAgent.${key}`];
    }),
    update: jest.fn().mockResolvedValue(undefined)
  }),
  workspaceFolders: undefined,
  fs: {
    readFile: jest.fn(),
    writeFile: jest.fn(),
    stat: jest.fn(),
    createDirectory: jest.fn(),
    delete: jest.fn()
  }
};

export const window = {
  showInformationMessage: jest.fn(),
  showErrorMessage: jest.fn(),
  showWarningMessage: jest.fn(),
  createWebviewPanel: jest.fn(),
  registerWebviewViewProvider: jest.fn(),
  activeTextEditor: undefined
};

export const commands = {
  registerCommand: jest.fn()
};

export const Uri = {
  file: jest.fn((path: string) => ({ fsPath: path })),
  parse: jest.fn((uri: string) => ({ toString: () => uri })),
  joinPath: jest.fn((base: any, ...paths: string[]) => {
    const basePath = base?.fsPath || '';
    return { fsPath: [basePath, ...paths].join('/'), path: [basePath, ...paths].join('/') };
  })
};

export const ViewColumn = {
  One: 1,
  Two: 2,
  Three: 3
};

export const ConfigurationTarget = {
  Global: 1,
  Workspace: 2,
  WorkspaceFolder: 3
};
