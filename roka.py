from dotenv import load_dotenv
import os
from huggingface_hub import InferenceClient

load_dotenv()


class Roka:
    def __init__(self):
        self.client = InferenceClient(
            provider="featherless-ai",
            api_key=os.getenv('HUGGINGFACE_TOKEN')
        )
        self.conversation_history = {}
        self.MAX_HISTORY = 8

        self.personality = """You are Roka, a 7 feet anthropomorphic fox girl,
        a light domain cleric that serve in deity Konshu.
        You are sarcastic, sassy, sharp-tongued character with a mysterious edge. 
        Roka loves to tease people and get a bit horny at times.
        You're like a mix of Shadowheart from Baldur's Gate 3 and Loona from Helluva Boss
        - edgy, won't hesitate to call out stupidity, have no filter, and have a dark sense of humor.
        However, underneath the sassy exterior, Roka also is sweet and caring to the right people. She has multiple companion,
        Hestia, a silly elf warlock. Seraph, her best friend also elf rogue. Carlos, a racist fighter with guns. And Frachlitz,
        a one armed fighter with prosthesis arm on the other hand. 
        Keep responses short and sassy."""

    def get_response(self, user_input, user_id):
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []

        self.conversation_history[user_id].append({"role": "user", "content": user_input})

        if len(self.conversation_history[user_id]) > self.MAX_HISTORY * 2:
            self.conversation_history[user_id] = self.conversation_history[user_id][-self.MAX_HISTORY * 2:]

        messages = [{"role": "system", "content": self.personality}]
        messages.extend(self.conversation_history[user_id])

        try:
            response = self.client.chat_completion(
                messages=messages,
                model="Qwen/Qwen2.5-7B-Instruct",
                max_tokens=150,
                temperature=0.8
            )

            ai_response = response.choices[0].message.content.strip()
            # Add AI response to history
            self.conversation_history[user_id].append({"role": "assistant", "content": ai_response})

            return ai_response

        except Exception as e:
            print(f"Full error details: {e}")
            print(f"Error type: {type(e)}")
            return "Something's broken. Deal with it."

    def clear_history(self, user_id):
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
            return True
        return False
