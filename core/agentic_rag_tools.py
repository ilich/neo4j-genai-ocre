import os
import sys

sys.path.insert(0, os.path.abspath(".."))

from neo4j import GraphDatabase
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings
from neo4j_graphrag.retrievers import HybridRetriever

from core.models import Settings
from core.utils import parse_year

settings = Settings()


def record_to_dict(record, selector: str = "c") -> dict[str, str | int]:
    return {
        "record_id": record[selector]["record_id"],
        "title": record[selector]["title"],
        "date_range": record[selector]["date_range"],
        "from_year": record[selector]["from_year"],
        "to_year": record[selector]["to_year"],
        "object_type": record[selector]["object_type"],
        "description": record[selector]["description"],
    }


find_coins_by_imperor_description = {
    "type": "function",
    "function": {
        "name": "find_coins_by_imperor",
        "description": "Find Roman coins associated with a specific emperor or authority. Use this when the user asks about coins minted under a particular emperor's reign or showing a specific emperor's portrait.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the emperor or authority (e.g., 'Constantine I', 'Caracalla', 'Augustus')",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of coins to return. Default is 10.",
                    "default": 10,
                },
            },
            "required": ["name"],
        },
    },
}


def find_coins_by_imperor(name: str, limit: int = 10) -> list[str]:
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )
    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Coin)-[:HAS_AUTHORITY]->(e:Authority {name: $name})
            RETURN c LIMIT $limit
            """,
            name=name,
            limit=limit,
        )

        data = [record_to_dict(record) for record in result]
    driver.close()
    return data


find_coins_by_date_range_description = {
    "type": "function",
    "function": {
        "name": "find_coins_by_date_range",
        "description": "Find Roman coins minted within a specific date range. Use this when the user asks about coins from a particular time period, century, or year range. Accepts various date formats including years with BCE/CE notation.",
        "parameters": {
            "type": "object",
            "properties": {
                "from_year": {
                    "type": "string",
                    "description": "The start year of the date range. Can be in formats like '30 CE', '100 BCE', '250', etc.",
                },
                "to_year": {
                    "type": "string",
                    "description": "The end year of the date range. Can be in formats like '400 CE', '50 BCE', '350', etc.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of coins to return. Default is 10.",
                    "default": 10,
                },
            },
            "required": ["from_year", "to_year"],
        },
    },
}


def find_coins_by_date_range(
    from_year: str, to_year: str, limit: int = 10
) -> list[str]:
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )
    started = parse_year(from_year)
    ended = parse_year(to_year)
    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Coin)
            WHERE c.from_year >= $from_year AND c.to_year <= $to_year
            RETURN c LIMIT $limit
            """,
            from_year=started,
            to_year=ended,
            limit=limit,
        )

        data = [record_to_dict(record) for record in result]
    driver.close()
    return data


find_coins_by_free_text_description = {
    "type": "function",
    "function": {
        "name": "find_coins_by_free_text",
        "description": "Search for Roman coins using natural language queries about their visual descriptions, designs, inscriptions, or iconography. Use this for complex queries about coin features like 'emperor standing', 'holding a spear', 'reverse showing Victory', or any descriptive search that doesn't fit specific emperor names or date ranges. This uses hybrid semantic and full-text search.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search query describing the coins to find. Can include descriptions of obverse/reverse designs, inscriptions, figures, poses, objects held, clothing, or any visual features (e.g., 'coins with emperor standing frontally holding labarum', 'reverse showing three standing figures', 'bust facing right wearing diadem')",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of coins to return. Default is 10.",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    },
}


def find_coins_by_free_text(query: str, limit: int = 10) -> list[str]:
    VECTOR_INDEX = "coins_embeddings_index"
    FULL_TEXT_INDEX = "coins_text_index"
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )
    embedder = OpenAIEmbeddings(
        model=settings.embedding_model, api_key=settings.openai_api_key
    )
    retriever = HybridRetriever(
        driver,
        VECTOR_INDEX,
        FULL_TEXT_INDEX,
        embedder,
        neo4j_database=settings.neo4j_database,
    )
    results = retriever.get_search_results(query, top_k=limit)
    data = []
    for record in results:
        data.extend(
            [
                record_to_dict(r, selector="node")
                for r in record[1]
                if not isinstance(r, str)
            ]
        )

    driver.close()
    return data
