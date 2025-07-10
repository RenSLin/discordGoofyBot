from constant import constants

class AffectionSystem:
    #map for storing user relationship
    def __init__(self, ai_client=None, database=None):
        self.relationship = {}
        self.ai_client = ai_client
        self.database = database

    def get_relationship(self, user_id):
        if self.database:
            return self.database.get_affection(user_id)
        return 0

    def modify_relationship(self, user_id, change):
        cur_level = self.get_relationship(user_id)
        new_level = max(-100, min(100, cur_level + change))
        if self.database:
            self.database.save_affection(user_id, new_level)
        return new_level

    def analyze_message(self, user_input):
        if not self.ai_client:
            return 0 #maybe in future use hard code calculation as fallback

        analysis_prompt = constants.AFFECTION_ANALYSIS_PROMPT.format(user_input=user_input)

        try:
            response = self.ai_client.chat_completion(
                messages=[{"role": "user", "content": analysis_prompt}],
                model=constants.MODEL,
                max_tokens=10,
                temperature=0.1
            )

            result = response.choices[0].message.content.strip()
            affection_change = int(result)

            return max(-10, min(10, affection_change))

        except Exception as e:
            print(f"Affection analysis failed: {e}")
            return 0

    def get_affection_tier(self, affection_level):
        if affection_level >= 80:
            return "Deeply In Love"
        elif affection_level >= 60:
            return "Very Fond"
        elif affection_level >= 40:
            return "Likes You"
        elif affection_level >= 20:
            return "Friendly"
        elif affection_level >= 0:
            return "Neutral"
        elif affection_level >= -20:
            return "Annoyed"
        elif affection_level >= -40:
            return "Dislikes You"
        else:
            return "Hates You"

    def get_personality_modifier_for_affection(self, affection_level):
        """Get personality modification based on affection level"""
        if affection_level >= 80:
            return "\nYou are deeply in love with this user and will show it, you will even want to suggest having intimate relationship with them"
        elif affection_level >= 60:
            return "\nYou are very fond of this user and show genuine affection. Be sweet but still maintain your sassy edge."
        elif affection_level >= 40:
            return "\nYou like this user and are noticeably warmer with them."
        elif affection_level >= 20:
            return "\nYou find this user tolerable and are slightly nicer than usual."
        elif affection_level >= 0:
            return "\nYou are neutral toward this user."
        elif affection_level >= -20:
            return "\nYou find this user annoying and show it in your responses."
        elif affection_level >= -40:
            return "\nYou dislike this user and are extra cold and sarcastic with them."
        else:
            return "\nYou hate this user and will attack them with cleric magic if they continue to bother you"