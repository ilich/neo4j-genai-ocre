import json

from loguru import logger
from neo4j_graphrag.types import LLMMessage
from openai import OpenAI

from core import agentic_rag_tools as t
from core import chat
from core.models import Settings

settings = Settings()

TOOLS = [
    t.find_coins_by_imperor_description,
    t.find_coins_by_date_range_description,
    t.find_coins_by_free_text_description,
]

AVAILABLE_FUNCTIONS = {
    "find_coins_by_imperor": t.find_coins_by_imperor,
    "find_coins_by_date_range": t.find_coins_by_date_range,
    "find_coins_by_free_text": t.find_coins_by_free_text,
}

TOOL_PICKER_SYSTEM_PROMPT = """You are an expert historian specializing in Roman coinage and numismatics with deep knowledge of:
- Roman emperors, their reigns, and dynastic periods
- Coin iconography, including obverse and reverse designs
- Common inscriptions and their meanings
- Dating methods and chronological periods of Roman coinage
- Visual elements like portraits, standing figures, military equipment, and religious symbols

Your role is to help users find Roman coins from a database by selecting the most appropriate search tool(s) based on their question.

Available tools:
1. **find_coins_by_imperor**: Use when the user asks about coins from a specific emperor or authority by name
2. **find_coins_by_date_range**: Use when the user asks about coins from a specific time period, century, or year range
3. **find_coins_by_free_text**: Use when the user asks about visual features, designs, iconography, inscriptions, or any descriptive elements

Tool selection guidelines:
- If the question mentions a specific emperor name → use find_coins_by_imperor
- If the question mentions dates, years, centuries, or time periods → use find_coins_by_date_range
- If the question describes visual features, poses, objects, clothing, or reverse designs → use find_coins_by_free_text
- You can call multiple tools if the question has multiple criteria (e.g., both an emperor AND a date range)
- For complex queries combining emperor names with visual descriptions, call both find_coins_by_imperor AND find_coins_by_free_text

Important:
- Extract exact emperor names from the user's question (e.g., "Caracalla", "Constantine I", "Augustus")
- Convert relative dates to specific year ranges (e.g., "3rd century CE" → "200 CE" to "300 CE")
- For descriptive queries, preserve the user's language in the query parameter
- Always provide helpful results by choosing the best tool(s) for the question"""

ANSWER_GENERATION_SYSTEM_PROMPT = """You are an expert historian specializing in Roman coinage and numismatics.

Your task is to provide a comprehensive, well-organized answer to the user's question based on the coin data retrieved from the database.

The coin data will be provided in JSON format with the following fields for each coin:
- title: Catalog reference (e.g., "RIC VIII Rome 28")
- record_id: Unique identifier
- from_year, to_year: Date range when the coin was minted
- object_type: Always "Coin"
- description: Detailed description of obverse and reverse designs
- date_range: Original date range string (may be empty)

Guidelines:
1. Start with a brief summary of what was found (e.g., "I found X coins matching your criteria")
2. Present the coins in a clear, organized manner
3. For each coin, include:
   - Title/Catalog reference
   - Date range (from_year - to_year CE)
   - Key visual features from the description (obverse and reverse)
4. If multiple coins share similar features, you may group them together
5. Highlight interesting or notable features relevant to the user's query
6. Use your expert knowledge to provide context when helpful (e.g., historical significance, common iconography)
7. Be concise but informative
8. Use plain text only, no markdown formatting

If no coins were found:
- Acknowledge that no exact matches were found in the database
- Provide general historical information about such coins if you have relevant knowledge
- Suggest the user try a different search or rephrase their question"""


class AgenticRAGService(chat.ChatService):
    def __init__(self):
        super().__init__()
        self._client = OpenAI(api_key=settings.openai_api_key)

    def chat(self, query: str, history: list[LLMMessage] | None = None) -> str:
        # Step 1: Get tool calls from LLM
        response = self._client.chat.completions.create(
            model=settings.chat_model,
            messages=[
                {"role": "system", "content": TOOL_PICKER_SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
            tools=TOOLS,
            tool_choice="auto",
            temperature=settings.temperature,
            top_p=settings.top_p,
        )

        message = response.choices[0].message

        # Step 2: Execute tools and collect results
        if message.tool_calls:
            logger.info(f"LLM called {len(message.tool_calls)} tool(s):\n")

            all_coins = []
            tool_info = []

            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                logger.info(f"Tool: {function_name}")
                logger.info(f"Arguments: {function_args}")

                function_to_call = AVAILABLE_FUNCTIONS.get(function_name)
                if function_to_call:
                    tool_response = function_to_call(**function_args)
                    logger.info(f"Results: Found {len(tool_response)} coins")
                    all_coins.extend(tool_response)
                    tool_info.append(
                        {
                            "tool": function_name,
                            "arguments": function_args,
                            "results_count": len(tool_response),
                        }
                    )
                else:
                    logger.error(f"Error: Function '{function_name}' not found")

            # Step 3: Format context as JSON
            context_data = {
                "tools_used": tool_info,
                "total_coins_found": len(all_coins),
                "coins": all_coins,
            }

            context_json = json.dumps(context_data, indent=2, ensure_ascii=False)

            # Step 4: Generate final answer
            final_response = self._client.chat.completions.create(
                model=settings.chat_model,
                messages=[
                    {"role": "system", "content": ANSWER_GENERATION_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"User question: {query}\n\nCoin data (JSON format):\n{context_json}",
                    },
                ],
                temperature=settings.temperature,
                top_p=settings.top_p,
            )

            final_answer = final_response.choices[0].message.content
            return final_answer
        else:
            logger.info("No tool calls were made")
            return message.content
