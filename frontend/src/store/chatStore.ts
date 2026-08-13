import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { SurfaceState } from "../a2ui/types";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  text: string;
  ts: string;
  domain?: string;
  surfaceId?: string;
  surface?: SurfaceState;
};

type ChatStore = {
  messages: ChatMessage[];
  activeTurnId: string | null;
  addUser: (text: string) => string;
  addAssistant: (payload: { text: string; domain?: string; surfaceId?: string; surface?: SurfaceState }) => string;
  setActiveTurn: (id: string | null) => void;
  clearHistory: () => void;
  historyForApi: () => Array<{ role: "user" | "assistant"; content: string }>;
};

export const useChatStore = create<ChatStore>()(
  persist(
    (set, get) => ({
      messages: [],
      activeTurnId: null,
      addUser: (text) => {
        const id = crypto.randomUUID();
        set({
          messages: [...get().messages, { id, role: "user", text, ts: new Date().toISOString() }],
          activeTurnId: id,
        });
        return id;
      },
      addAssistant: ({ text, domain, surfaceId, surface }) => {
        const id = crypto.randomUUID();
        set({
          messages: [
            ...get().messages,
            {
              id,
              role: "assistant",
              text,
              ts: new Date().toISOString(),
              domain,
              surfaceId,
              surface: surface ? structuredClone(surface) : undefined,
            },
          ],
          activeTurnId: id,
        });
        return id;
      },
      setActiveTurn: (id) => set({ activeTurnId: id }),
      clearHistory: () => set({ messages: [], activeTurnId: null }),
      historyForApi: () =>
        get()
          .messages.slice(-12)
          .map((m) => ({ role: m.role, content: m.text })),
    }),
    {
      name: "a2ui-demo-chat",
      partialize: (s) => ({ messages: s.messages.slice(-30), activeTurnId: s.activeTurnId }),
    },
  ),
);
