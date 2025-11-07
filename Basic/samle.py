rom openai import OpenAI
import oracledb  # Oracle database client

# Initialize OpenAI client
client = OpenAI(api_key="sk-proj-...")  # Use your API key

# ✅ Oracle connection setup
# Example DSN: "hostname:port/service_name"
dsn = "your-hostname:1521/yourservicename"

# Connect to Oracle
conn = oracledb.connect(
    user="your_username",
    password="your_password",
    dsn=dsn
)
cursor = conn.cursor()

def ask_database(question):
    """
    Convert a natural language question into SQL using GPT,
    run the query, and return results.
    """

    prompt = f"""
You are an assistant that writes SQL queries for an Oracle database.
The database has the following tables:

customers(id, name, email, city)
products(id, name, category, price)
orders(id, customer_id, product_id, quantity, order_date)

Relationships:
- orders.customer_id references customers.id
- orders.product_id references products.id

Rules:
- Always use JOINs correctly.
- To calculate revenue: SUM(products.price * orders.quantity)
- Always group by customer name when showing per-customer data.
- When searching by name, or text fields, use
  LIKE '%%keyword%%' instead of '=' for partial matches.
- Return only the SQL query (no markdown, no explanations).

User question: "{question}"
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    sql_query = response.choices[0].message.content.strip()

    # Clean up potential markdown formatting
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

    print("🧩 Generated SQL:", sql_query)

    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        return results
    except Exception as e:
        return f"Error running SQL: {e}"


# Example loop
while True:
    question = input("Ask your database: ")
    if question.lower() in ["exit", "quit"]:
        break
    answer = ask_database(question)
    print("💡 Answer:", answer)