from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import json
import pandas as pd
from dotenv import load_dotenv
import duckdb
import os

# Load API keys from .env
load_dotenv()
GROQ_API = os.environ.get('GROQ_API')


class FinancialSummary(BaseModel):
    summarized_content: str = Field(
        description="Short summary of post content")
    summarized_comments: str = Field(description="Summary of comments")
    verdict: str = Field(description="BUY, SELL, or HOLD based on sentiment")


def summarize_using_langchain(TABLE_NAME):
    con = duckdb.connect("data/duckdb/pennyai.duckdb")

    df = con.execute(f"""
    SELECT row_id, content, comments
    FROM {TABLE_NAME}
    WHERE summarized_content IS NULL
    OR summarized_content = ''
    """).fetchdf()

    print(f"Processing {len(df)} rows...")

    # Initialize LLM
    llm = ChatGroq(model="llama-3.1-8b-instant",
                   temperature=0, api_key=GROQ_API)

    # Setup JSON parser
    parser = JsonOutputParser(pydantic_object=FinancialSummary)

    # Prompt template
    prompt_template = """You are a financial analyst AI. 
        Summarize the Reddit post content and comments. 

        Post content:
        {content}

        Comments:
        {comments}

        {format_instructions}
        """

    prompt = ChatPromptTemplate.from_template(prompt_template)

    # Create chain using LCEL
    chain = prompt | llm | parser

    # Process each row
    results = []
    for idx, row in df.iterrows():
        content = row['content'] or ""

        # Handle comments - could be list or string
        if isinstance(row['comments'], list):
            comments = " ".join(row['comments'])
        else:
            comments = str(row['comments']) if row['comments'] else ""

        try:
            output = chain.invoke({
                "content": content,
                "comments": comments,
                "format_instructions": parser.get_format_instructions()
            })

            results.append({
                "row_id": row['row_id'],
                "summarized_content": output.get("summarized_content", ""),
                "summarized_comments": output.get("summarized_comments", ""),
                "verdict": output.get("verdict", "")
            })

            print(f"✓ Processed row {idx + 1}/{len(df)}")

        except Exception as e:
            print(f"✗ Error processing row {row['row_id']}: {e}")
            results.append({
                "row_id": row['row_id'],
                "summarized_content": "",
                "summarized_comments": "",
                "verdict": ""
            })

    # Create summary DataFrame
    summary_df = pd.DataFrame(results)

    # Register as temporary table in DuckDB
    con.register("temp_summary", summary_df)

    # Update original table
    con.execute(f"""
    UPDATE {TABLE_NAME} AS t
    SET
        summarized_content = s.summarized_content,
        summarized_comments = s.summarized_comments,
        verdict = s.verdict
    FROM temp_summary AS s
    WHERE t.row_id = s.row_id
    """)

    con.commit()
    con.close()

    print(f"✅ Successfully updated {len(results)} rows in {TABLE_NAME}")
