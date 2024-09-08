from flask import Flask, request, jsonify
import warnings
import numpy as np
from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer
import psycopg2
from flask_cors import CORS


# Suppress specific FutureWarning
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers.tokenization_utils_base")

# Initialize Flask app
app = Flask(__name__)
CORS(app)


# Load SBERT model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# PostgreSQL connection details
POSTGRES_HOST = "localhost"
POSTGRES_DB = "mydatabase"
POSTGRES_USER = "shravan"
POSTGRES_PASSWORD = "shravan8754"

def get_most_similar_answer(user_query, table_name='qa_table'):
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

        # Format embedding as a string to use in SQL
        query_embedding_str = np.array2string(query_embedding, separator=',')[1:-1]

        query = f"""
        SELECT question, answer
        FROM {table_name}
        ORDER BY embedding <-> '[{query_embedding_str}]'::vector
        LIMIT 1;
        """
        
        cur.execute(query)
        result = cur.fetchone()
        conn.close()

        if result:
            return {"question": result[0], "answer": result[1]}
        else:
            return {"error": "Sorry, I couldn't find a relevant answer."}
    
    except psycopg2.Error as e:
        print(f"Error occurred: {e}")
        return {"error": "Database error occurred."}

# Define an API endpoint
@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    user_query = data.get('query')
    if not user_query:
        return jsonify({"error": "No query provided"}), 400
        
    response = get_most_similar_answer(user_query)
    return jsonify(response)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
