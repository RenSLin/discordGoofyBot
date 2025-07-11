from dotenv import load_dotenv
import os
from character import affection
from constant import constants
from huggingface_hub import InferenceClient
from bs4 import BeautifulSoup
import urllib.parse
import requests
from db import RokaDatabase
load_dotenv()


class Roka:
    def __init__(self):
        self.client = InferenceClient(
            provider="fireworks-ai",
            api_key=os.getenv('HUGGINGFACE_TOKEN')
        )
        self.db = RokaDatabase()
        self.MAX_HISTORY = 10
        self.personality = constants.PERSONALITY
        self.affection_system = affection.AffectionSystem(self.client, self.db)

    def get_response(self, user_input, user_id, affection_prompt):

        self.db.save_message(user_id, "user", user_input)
        history = self.db.get_chat_history(user_id)

        messages = [{"role": "system", "content": self.personality + affection_prompt}]
        messages.extend(history)

        try:
            response = self.client.chat_completion(
                messages=messages,
                model=constants.MODEL,
                max_tokens=180,
                temperature=0.7
            )

            ai_response = response.choices[0].message.content.strip()
            # Add AI response to history
            self.db.save_message(user_id, "assistant", ai_response)

            return ai_response

        except Exception as e:
            print(f"Full error details: {e}")
            print(f"Error type: {type(e)}")
            return "Something's broken. Deal with it."

    def get_response_with_affection(self, user_input, user_id):
        affection_change = self.affection_system.analyze_message(user_input)
        new_affection = self.affection_system.modify_relationship(user_id, affection_change)
        affection_modifier = self.affection_system.get_personality_modifier_for_affection(new_affection)
        return self.get_response(user_input, user_id, affection_modifier)

    def web_search(self, query):
        try:
            search_url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            results = soup.find_all('a', class_='result__a')[:3]

            if results:
                search_results = []
                for result in results:
                    title = result.get_text().strip()
                    link = result.get('href')
                    search_results.append(f"• **{title}**\n  {link}")

                return f"Search results for '{query}':**\n" + "\n\n".join(search_results)
            else:
                return f"No results found for '{query}'"


        except Exception as e:
            print(f"Full error details: {e}")
            return "Web search error. Deal with it."

    def clear_history(self, user_id):
        return self.db.clear_chat_history(user_id)
