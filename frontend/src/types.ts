export interface ChatRequest {
  user_id: string;
  session_id: string;
  message: string;
  department?: string;
}

export interface AgentStep {
  step: number;
  thought: string;
  action: string;
  action_input: Record<string, unknown>;
  observation: unknown;
}

export interface SearchHit {
  content: string;
  metadata: Record<string, unknown>;
}

export interface ChatResponse {
  session_id: string;
  answer: string;
  trace: AgentStep[];
  retrieval_preview: SearchHit[];
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface UiMessage {
  role: 'user' | 'assistant';
  content: string;
  trace?: AgentStep[];
}
