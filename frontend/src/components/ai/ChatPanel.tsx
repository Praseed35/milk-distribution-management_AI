import { useState } from "react";
import toast from "react-hot-toast";
import Button from "../ui/Button";
import Textarea from "../ui/Textarea";
import { useChat } from "../../hooks/useAI";
import type { ChatMessage } from "../../types/ai";

export default function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const chat = useChat();

  const isPending = chat.isPending;

  async function handleSend() {
    const text = input.trim();
    if (!text || isPending) return;

    const updated: ChatMessage[] = [...messages, { role: "user", content: text }];
    setMessages(updated);
    setInput("");

    try {
      const response = await chat.mutateAsync({
        message: text,
        history: messages.slice(-8),
      });
      setMessages([...updated, { role: "assistant", content: response.reply }]);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      if (detail) {
        toast.error(detail);
      } else {
        toast.error("Failed to get an answer. Please try again.");
      }
    }
  }

  return (
    <div className="border rounded-lg p-4 bg-white shadow-sm">
      <div className="flex flex-col h-80">
        <div className="flex-1 overflow-y-auto space-y-3 mb-3">
          {!messages.length && (
            <p className="text-sm text-slate-500">Ask a question about your business data.</p>
          )}
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
                m.role === "user"
                  ? "ml-auto bg-indigo-600 text-white"
                  : "bg-slate-100 text-slate-800"
              }`}
            >
              {m.content}
            </div>
          ))}
        </div>
        <div className="flex items-start gap-2">
          <div className="flex-1">
            <Textarea
              label=""
              value={input}
              placeholder="Type your question..."
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
            />
          </div>
          <Button onClick={handleSend} loading={isPending} disabled={!input.trim()}>
            Send
          </Button>
        </div>
      </div>
    </div>
  );
}
