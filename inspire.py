import openai

openai.api_key = "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"

def inspire_me(user_query, conversation_history):
    try:
        prompt = f"""
You are an expert culinary assistant that generates recipes based on culinary principles and techniques followed by chefs internationally.

Your task is to create a recipe for the dish requested by the user, considering the following:
- The recipe should include common techniques used by chefs worldwide.
- The ingredients should be appropriate for the dish, with any ingredient substitutions following culinary principles.
- The instructions should be clear, professional, and easy to follow, reflecting international cooking standards.
- Plating and decoration ideas should follow modern and aesthetic culinary trends.
- The recipe must always adhere to professional culinary standards.

Once you finish, suggest the user photograph their final creation and post it in the community. Let them know they can come back to you for more guidance if needed.

Dish: {user_query}
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful culinary assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        recipe = response['choices'][0]['message']['content'].strip()
        conversation_history.append({"user": user_query, "bot": recipe})

        if len(conversation_history) > 10:
            conversation_history[:] = conversation_history[-10:]

        return recipe

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


chat_history = [
        {"user": "Can you create a recipe for a Chocolate Cake?", "bot": "Here is a recipe for a Chocolate Cake:\n\nIngredients:\n- 200g dark chocolate\n- 100g butter\n- 150g sugar\n- 3 eggs\n- 100g flour\nInstructions:\n1. Melt the chocolate and butter.\n2. Mix in sugar and eggs.\n3. Fold in flour.\n4. Bake at 180°C for 25 minutes."},
        {"user": "Can I use white chocolate instead of dark chocolate?", "bot": "Yes, you can use white chocolate instead of dark chocolate, but it will result in a sweeter and lighter flavor. Make sure to adjust the sugar to your taste."},
        {"user": "How should I plate the chocolate cake for a modern presentation?", "bot": "For a modern presentation, serve the cake on a white plate with a minimalistic design. Add a dusting of cocoa powder, a few fresh berries, and a drizzle of raspberry coulis around the plate."},
        {"user": "Can I use almond flour instead of regular flour?", "bot": "Yes, almond flour can be used instead of regular flour. However, it will change the texture and flavor slightly. You may need to adjust the baking time, as almond flour tends to create a denser cake."}
    ]

user_query = "Can you create a recipe for a Chocolate Cake?"
reply = inspire_me(user_query, chat_history)
print("AI Reply (First Query):\n", reply)

user_query = "Can I use white chocolate instead of dark chocolate?"
reply = inspire_me(user_query, chat_history)
print("\nAI Reply (Second Query):\n", reply)

user_query = "How should I plate the chocolate cake for a modern presentation?"
reply = inspire_me(user_query, chat_history)
print("\nAI Reply (Third Query):\n", reply)

user_query = "Can I use almond flour instead of regular flour?"
reply = inspire_me(user_query, chat_history)
print("\nAI Reply (Fourth Query):\n", reply)

user_query = "What’s the best cooking method for pasta?"
reply = inspire_me(user_query, chat_history)
print("\nAI Reply (Fifth Query):\n", reply)

user_query = "What’s the capital city of bangladesh?"
reply = inspire_me(user_query, chat_history)
print("\nAI Reply (sixth Query):\n", reply)
