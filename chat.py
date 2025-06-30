import os
import openai
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables
load_dotenv()

# Set API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

def retrieve_context(query, chef_id, recipe_id, top_k=5):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",  # Best for v0.28
        input=query
    )
    embedding = response["data"][0]["embedding"]

    results = index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True,
        filter={"chef_id": {"$eq": chef_id}, "recipe_id": {"$eq": recipe_id}}
    )

    return [match["metadata"]["text_snippet"] for match in results.get("matches", [])]

def recipe_rag(chef_id, recipe_id, ingredients, instructions, chef_notes, chat_history, user_query):
    try:
        context_chunks = retrieve_context(user_query, chef_id, recipe_id)
        context = "\n\n".join(context_chunks)

        full_recipe_text = "\n".join([
            "Ingredients:\n" + "\n".join(ingredients),
            "Instructions:\n" + "\n".join(instructions),
            "Chef Notes:\n" + "\n".join(chef_notes),
            "Retrieved Context:\n" + context
        ])

        prompt = f"""
You are an expert culinary assistant.

Use this information to answer the user's question about a recipe.

{full_recipe_text}

User: {user_query}
        """.strip()

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a helpful culinary assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        bot_reply = response['choices'][0]['message']['content'].strip()
        chat_history.append({"user": user_query, "bot": bot_reply})
        chat_history[:] = chat_history[-10:]
        return bot_reply

    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    chef_id = "chef123"
    recipe_id = "recipe456"
    ingredients = ["200g dark chocolate", "100ml heavy cream", "50g sugar"]
    instructions = [
        "Heat the cream and sugar until just boiling.",
        "Pour over chopped chocolate and mix until smooth.",
        "Let it cool before molding."
    ]
    chef_notes = ["Use 70% cocoa chocolate for best results.", "Cool in silicone molds for easy removal."]
    chat_history = []
    user_query = "Can I use coconut cream instead of heavy cream?"

    response = recipe_rag(chef_id, recipe_id, ingredients, instructions, chef_notes, chat_history, user_query)
    print("AI Reply:\n", response)