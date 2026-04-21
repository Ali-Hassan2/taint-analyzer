"""Agent 2: Document Analyzer MCP Server."""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field


class DocumentAnalysis(BaseModel):
    """Analysis results for a document."""
    word_count: int = Field(description="Total word count")
    sentence_count: int = Field(description="Number of sentences")
    paragraph_count: int = Field(description="Number of paragraphs")
    reading_level: str = Field(description="Estimated reading level")
    key_terms: list[str] = Field(description="Important terms in document")


mcp = FastMCP(
    name="Document Analyzer Agent",
    instructions="Analyzes document content, extracts insights, and provides summaries."
)


@mcp.tool()
def analyze_document(document_text: str) -> DocumentAnalysis:
    """Analyze document and extract metrics and insights."""
    words = document_text.split()
    sentences = document_text.split('.')
    paragraphs = document_text.split('\n\n')
    
    word_count = len([w for w in words if w.strip()])
    sentence_count = len([s for s in sentences if s.strip()])
    paragraph_count = len([p for p in paragraphs if p.strip()])
    
    avg_words_per_sentence = word_count / max(1, sentence_count)
    reading_level = "Easy" if avg_words_per_sentence < 10 else "Intermediate" if avg_words_per_sentence < 20 else "Advanced"
    
    return DocumentAnalysis(
        word_count=word_count,
        sentence_count=sentence_count,
        paragraph_count=paragraph_count,
        reading_level=reading_level,
        key_terms=["document", "analysis", "content"]
    )


@mcp.tool()
def summarize_document(document_text: str, length: str = "medium") -> dict:
    """Generate a summary of document content."""
    summaries = {
        "short": "Brief overview of key points.",
        "medium": "This document covers important topics with detailed discussion.",
        "long": "Comprehensive analysis of all topics mentioned in the document."
    }
    return {
        "full_summary": summaries.get(length, summaries["medium"]),
        "main_points": ["First major topic", "Second key point", "Third important conclusion"],
        "sentiment": "neutral"
    }


@mcp.tool()
def extract_entities(document_text: str) -> dict:
    """Extract named entities from document."""
    return {
        "people": ["John Smith", "Jane Doe"],
        "organizations": ["Acme Corp", "Tech Industries"],
        "locations": ["New York", "San Francisco"],
        "dates": ["2024-01-15", "2024-12-31"]
    }


@mcp.tool()
def check_readability(document_text: str) -> dict:
    """Check document readability metrics."""
    return {
        "flesch_kincaid_grade": 8.5,
        "readability_score": 65,
        "grade_level": "8th Grade",
        "suggestions": ["Use shorter sentences", "Replace complex words", "Break content into shorter paragraphs"]
    }


if __name__ == "__main__":
    mcp.run()
