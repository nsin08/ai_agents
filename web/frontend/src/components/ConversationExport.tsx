import React from "react";
import "./ConversationExport.css";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string | Date;
  metadata?: Record<string, unknown>;
}

interface ConversationExportProps {
  messages: Message[];
}

const ConversationExport: React.FC<ConversationExportProps> = ({ messages }) => {
  const exportAsJSON = () => {
    const dataStr = JSON.stringify(messages, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `conversation-${new Date().toISOString()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const exportAsMarkdown = () => {
    let markdown = `# AI Agent Conversation\n\n`;
    markdown += `**Exported:** ${new Date().toLocaleString()}\n\n`;
    markdown += `---\n\n`;

    messages.forEach((msg) => {
      const timestamp = new Date(msg.timestamp).toLocaleTimeString();
      markdown += `## ${msg.role === "user" ? "👤 User" : "🤖 Assistant"} (${timestamp})\n\n`;
      markdown += `${msg.content}\n\n`;
      
      if (msg.metadata && Object.keys(msg.metadata).length > 0) {
        markdown += `<details>\n<summary>Metadata</summary>\n\n\`\`\`json\n${JSON.stringify(msg.metadata, null, 2)}\n\`\`\`\n</details>\n\n`;
      }
      
      markdown += `---\n\n`;
    });

    const dataBlob = new Blob([markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `conversation-${new Date().toISOString()}.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="export-controls">
      <button
        className="export-button export-json"
        onClick={exportAsJSON}
        disabled={messages.length === 0}
        title="Export as JSON"
      >
        📄 Export JSON
      </button>
      <button
        className="export-button export-markdown"
        onClick={exportAsMarkdown}
        disabled={messages.length === 0}
        title="Export as Markdown"
      >
        📝 Export Markdown
      </button>
    </div>
  );
};

export default ConversationExport;
