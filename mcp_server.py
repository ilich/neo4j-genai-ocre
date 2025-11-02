from dotenv import load_dotenv
from fastmcp import FastMCP

from core.ocre_agent import AgenticRAGService

load_dotenv()


mcp = FastMCP(
    "roman-numismatics-assistant",
    instructions="""
This MCP server provides access to the Online Coins of the Roman Empire (OCRE) database through an agentic RAG system.

The server specializes in:
- Finding Roman coins by emperor/authority name
- Searching coins by date ranges (with flexible date parsing supporting BCE/CE notation)
- Performing semantic searches on coin descriptions, iconography, and visual features
- Providing expert historical context about Roman coinage

The system uses an intelligent tool selection mechanism that automatically chooses the most appropriate search method(s) based on your query. It can combine multiple search strategies for complex queries (e.g., finding coins of a specific emperor within a date range).

Query examples:
- "Find coins of Constantine I from the 4th century"
- "Show me coins with an emperor standing frontally holding a labarum"
- "What coins were minted between 200 and 300 CE?"
- "Find Caracalla coins with military imagery on the reverse"

The server returns comprehensive answers with catalog references (RIC), dates, and detailed descriptions of obverse and reverse designs, all contextualized by expert numismatic knowledge.
    """.strip()
)


@mcp.tool
def describe_roman_coins(query: str) -> str:
    """
    Search and retrieve information about Roman coins from the OCRE database.

    This tool uses an intelligent agentic RAG system that automatically selects
    the most appropriate search strategy based on your query. It can search by
    emperor name, date range, or visual/iconographic features, and will combine
    multiple search methods when needed for complex queries.

    Args:
        query: Natural language question or search request about Roman coins.
               Can include emperor names, date ranges, visual descriptions,
               or any combination of these criteria.

    Returns:
        A comprehensive answer with detailed information about matching coins,
        including catalog references (RIC), minting dates, and descriptions
        of obverse and reverse designs, all contextualized with expert
        numismatic knowledge.

    Examples:
        - "Find coins of Constantine I from the 4th century"
        - "Show me coins with an emperor standing frontally holding a labarum"
        - "What coins were minted between 200 and 300 CE depicting Caracalla?"
        - "Find coins with Victory on the reverse from the 3rd century"
    """
    agent = AgenticRAGService()
    return agent.chat(query)


if __name__ == "__main__":
    mcp.run()
