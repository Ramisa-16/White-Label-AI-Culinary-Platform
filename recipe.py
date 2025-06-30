import os
import traceback
import openai
import docx
import pandas as pd
import fitz
import textract

openai.api_key = "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"

def extract_text_from_file(file_path):
    try:
        if file_path.endswith(".pdf"):
            doc = fitz.open(file_path)
            return "\n".join(page.get_text() for page in doc)
        elif file_path.endswith(".docx"):
            doc = docx.Document(file_path)
            return "\n".join(para.text for para in doc.paragraphs)
        elif file_path.endswith(".doc"):
            return textract.process(file_path).decode("utf-8")
        else:
            return ""
    except Exception as e:
        print(f"Error extracting text from file {file_path}: {str(e)}")
        return ""


def extract_text_from_xlsx(xlsx_path):
    try:
        df = pd.read_excel(xlsx_path)
        return df.to_string(index=False)
    except Exception as e:
        print(f"Error extracting text from Excel file {xlsx_path}: {str(e)}")
        return ""


def recipe(file_path=None, xlsx_path=None, ingredients=None, instructions=None, chef_notes=None, chat_history=None, user_query=None):
    try:
        ingredients = ingredients if ingredients else []
        instructions = instructions if instructions else []
        chef_notes = chef_notes if chef_notes else []
        chat_history = chat_history if chat_history else []

        if len(chat_history) > 10:
            chat_history = chat_history[-10:]
        file_texts = []

        if file_path:
            if file_path.endswith(".pdf") and os.path.exists(file_path):
                file_texts.append(extract_text_from_file(file_path))
            elif file_path.endswith(".docx") and os.path.exists(file_path):
                file_texts.append(extract_text_from_file(file_path))
            elif file_path.endswith(".doc") and os.path.exists(file_path):
                file_texts.append(extract_text_from_file(file_path))

        if xlsx_path and os.path.exists(xlsx_path):
            file_texts.append(extract_text_from_xlsx(xlsx_path))
        file_text = "\n".join(file_texts)
        full_recipe_text = "\n".join([
            "Ingredients:\n" + "\n".join(ingredients),
            "Instructions:\n" + "\n".join(instructions),
            "Chef Notes:\n" + "\n".join(chef_notes),
            "File Content:\n" + file_text
        ])
        
        prompt = f"""
You are an expert culinary assistant.

You may assist the user with:
- Ingredient substitutions {ingredients}
- Scaling quantities {ingredients}
- Presentation and plating ideas based on the recipe {instructions}
- Chef's style interpretation (based on chef notes {chef_notes})
- Decoration concepts (e.g., bonbon colors, airbrush patterns) {instructions}
- Answer based on {user_query} and {chat_history}
- If user asks about anything other than the recipe, you will explain your limits politely.

Here is the recipe:

{full_recipe_text}

User: {user_query}
        """.strip()

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful culinary assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        bot_reply = response['choices'][0]['message']['content'].strip()
        chat_history.append({"user": user_query, "bot": bot_reply})
        
        if len(chat_history) > 10:
            chat_history[:] = chat_history[-10:]

        return bot_reply

    except Exception as e:
        return f"An error occurred: {str(e)}\n{traceback.format_exc()}"


if __name__ == "__main__":
    file_path = r"C:\Users\Ramisa\Desktop\bman\Digital ocean .pdf"
    xlsx_path = r""
    ingredients = [
        "200g dark chocolate",
        "100ml heavy cream",
        "50g sugar"
    ]
    instructions = [
        "Heat the cream and sugar until just boiling.",
        "Pour over chopped chocolate and mix until smooth.",
        "Let it cool before molding."
    ]
    chef_notes = [
        "Use 70% cocoa chocolate for best results.",
        "Cool in silicone molds for easy removal."
    ]
    chat_history = [
        {"user": "What can I use instead of heavy cream?", "bot": "You can substitute heavy cream with coconut cream or full-fat milk, but the texture might differ."},
        {"user": "Can I add a little vanilla extract?", "bot": "Yes, you can add 1/2 teaspoon of vanilla extract for extra flavor."},
        {"user": "What should I do if I don't have silicone molds?", "bot": "If you don't have silicone molds, you can use a metal tray lined with parchment paper. Just ensure the mixture doesn't stick."},
        {"user": "How can I make this recipe gluten-free?", "bot": "This recipe is naturally gluten-free as it doesn't contain flour. Just ensure your chocolate is certified gluten-free."},
        {"user": "Can I use white chocolate instead?", "bot": "White chocolate can be used, but keep in mind it has a much sweeter and milder flavor than dark chocolate."},
        {"user": "How long do I need to cool the chocolate mixture?", "bot": "Allow the chocolate mixture to cool for at least 30 minutes before molding, or until it thickens to a suitable consistency."},
        {"user": "Can I add nuts to this recipe?", "bot": "Yes, chopped nuts like hazelnuts or almonds would pair well with this chocolate mixture."},
        {"user": "Is this recipe good for making chocolate bonbons?", "bot": "Yes, this recipe is perfect for making chocolate bonbons. The mixture will set nicely in molds."},
        {"user": "What kind of chocolate should I use for best results?", "bot": "For best results, use 70% cocoa dark chocolate. It provides the best balance of richness and sweetness."},
        {"user": "Can I double this recipe?", "bot": "Yes, you can double the recipe. Just be sure to adjust your cooling time and mold size accordingly."}
    ]
    user_query = "Can I use white chocolate instead?"
    reply = recipe(file_path, xlsx_path, ingredients, instructions, chef_notes, chat_history, user_query)
    print("AI Reply:\n", reply)
