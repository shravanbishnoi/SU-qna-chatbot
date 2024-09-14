from flask import Flask, request, jsonify
import warnings
import numpy as np
from sentence_transformers import SentenceTransformer
import psycopg2
from flask_cors import CORS


# Suppress specific FutureWarning from the transformers library
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

# Function to fetch the most similar answer
def get_most_similar_answer(user_query, table_name='qa_table'):
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        cur = conn.cursor()

        # Compute the embedding for the user query
        query_embedding = model.encode([user_query])[0]

        # Convert embedding to string to insert in SQL query
        query_embedding_str = np.array2string(query_embedding, separator=',')[1:-1]

        # SQL query to fetch the most similar question and its similarity score
        query = f"""
        SELECT question, answer, embedding <-> '[{query_embedding_str}]'::vector AS similarity
        FROM {table_name}
        ORDER BY similarity
        LIMIT 1;
        """
        
        cur.execute(query)
        result = cur.fetchone()
        conn.close()

        # Check if result was found
        if result:
            question, answer, similarity_score = result
            # print(f"Similarity score for the query: {similarity_score:.6f}")
            # if similarity_score > 5:
            #     return {"error": "Sorry, I couldn't find a relevant answer. Could you rephrase that or provide more detail?"}            
            return {"question": question, "answer": answer, "similarity_score": similarity_score}
        else:
            return {"error": "Sorry, I couldn't find a relevant answer."}
    
    except psycopg2.Error as e:
        print(f"Error occurred: {e}")
        return {"error": "Database error occurred."}

# Define the chatbot API endpoint
@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    user_query = data.get('query')
    
    # If no query provided in the request, return an error
    if not user_query:
        return jsonify({"error": "No query provided"}), 400
    
    # Get the most similar answer based on the query
    response = get_most_similar_answer(user_query)
    
    # Return the response as JSON
    return jsonify(response)

# Start the Flask application
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
