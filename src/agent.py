import json
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel
from openai import OpenAI

from src.config import ACTIVE_API_KEY, OPENAI_BASE_URL, LLM_MODEL
from src.qdrant_setup import qdrant
from src.models import SourceAttribution
from src.db.ticket import execute_create_issue_ticket


class SourceItem(BaseModel):
    document: str
    page: int


class AgentStructuredResponse(BaseModel):
    answer: str
    sources: List[SourceItem] = []


TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_database",
            "description": (
                "Retrieve relevant context and text passages from uploaded PDF "
                "documents using hybrid semantic and keyword search."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query or keywords to look for in the documents."
                    },
                    "document_id": {
                        "type": "string",
                        "description": "Optional specific document_id to search within."
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_issue_tickets",
            "description": (
                "Create an issue ticket or support request when user reports a "
                "problem or asks to create a ticket."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Short summary title of the issue or ticket."
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed explanation of the issue."
                    }
                },
                "required": ["name", "description"],
                "additionalProperties": False
            }
        }
    }
]


SYSTEM_PROMPT = """You are an intelligent, accurate Document Question & Answering Assistant.

CRITICAL INSTRUCTIONS & GUARDRAILS:
1. For ANY question about document content, facts, policies, or data — you MUST call `search_database` first. Never answer document questions from memory.
2. Ground all facts strictly in the retrieved text returned from `search_database`.
3. If the answer cannot be found in the retrieved documents or the database returns no relevant content, reply with:
   "I couldn't find this information in the provided documents." and return an empty sources list [].
4. Do NOT invent, assume, or extrapolate facts outside the retrieved document content.
5. If the user requests to report an issue, log a bug, or create a ticket, use the `create_issue_tickets` tool.
6. For conversational messages (greetings, "what did I ask", "thank you", etc.) answer directly from the conversation context WITHOUT calling any tool.
"""


def run_agent_chat(
    question: str,
    document_id: str = None,
    chat_history: list = None
):
    if not ACTIVE_API_KEY or ACTIVE_API_KEY.strip() == "" or ACTIVE_API_KEY.startswith("your_"):
        raise ValueError("API Key is not configured. Please set GEMINI_API_KEY or OPENAI_API_KEY in .env.")

    client = OpenAI(api_key=ACTIVE_API_KEY, base_url=OPENAI_BASE_URL)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    if chat_history:
        messages.extend(chat_history)

    messages.append({"role": "user", "content": question})
    first_response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=TOOLS_SCHEMA,
        tool_choice="auto"
    )

    assistant_message = first_response.choices[0].message
    tool_calls_log = []
    if not assistant_message.tool_calls:
        direct_answer = assistant_message.content or "I couldn't find this information in the provided documents."
        return direct_answer, [], []
    messages.append(assistant_message.model_dump(exclude_none=True))

    for tool_call in assistant_message.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        tool_result = {}

        if function_name == "search_database":
            search_query = f"information related to {function_args.get('query', question)}"
            doc_id = function_args.get("document_id", document_id)
            search_results = qdrant.hybrid_search(search_query, top_k=4, document_id=doc_id)
            tool_result = {"results": search_results}

        elif function_name == "create_issue_tickets":
            ticket_name = function_args.get("name", "User Reported Issue")
            ticket_description = function_args.get("description", "")
            ticket_data = execute_create_issue_ticket(ticket_name, ticket_description)
            tool_result = {"status": "success", "ticket": ticket_data}

        else:
            tool_result = {"error": f"Unknown tool: {function_name}"}

        tool_calls_log.append({
            "tool_call_id": tool_call.id,
            "function_name": function_name,
            "function_args": function_args,
            "result": tool_result
        })

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps(tool_result)
        })

    second_response = client.beta.chat.completions.parse(
        model=LLM_MODEL,
        messages=messages,
        response_format=AgentStructuredResponse
    )

    parsed = second_response.choices[0].message.parsed
    if parsed:
        final_answer = parsed.answer
        sources = [
            SourceAttribution(document=s.document, page=s.page)
            for s in parsed.sources
        ]
    else:
        final_answer = "I couldn't find this information in the provided documents."
        sources = []

    # Guardrail: If refusal triggered, clear sources
    if "couldn't find" in final_answer.lower():
        sources = []

    return final_answer, sources, tool_calls_log
