import numpy as np
from sentence_transformers import SentenceTransformer
import psycopg2

# Constants
POSTGRES_HOST = "localhost"
POSTGRES_DB = "mydatabase"
POSTGRES_USER = "shravan"
POSTGRES_PASSWORD = "shravan8754"

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def get_response(user_query):
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        cur = conn.cursor()

        # Compute embedding for the user query
        query_embedding = model.encode([user_query])[0]

        # Convert embedding to string for SQL
        query_embedding_str = np.array2string(query_embedding, separator=',')[1:-1]

        # Query to find the most similar question
        cur.execute(f"""
            SELECT question, answer
            FROM qa_table
            ORDER BY embedding <-> '[{query_embedding_str}]'
            LIMIT 1;
        """)
        result = cur.fetchone()
        conn.close()

        if result:
            return result[1]  # Return the answer
        else:
            return "Sorry, I couldn't find a relevant answer."
    except Exception as e:
        return str(e)
