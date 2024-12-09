import openai
import json
from password_recommender import recommend_similar_passwords_from_csv  # Ensure this module is available

class StrongPasswordGenerator:
    def __init__(self, university_name, test_mode=False):
        self.university_name = university_name
        self.test_mode = test_mode  # Controls whether to enable test mode
        # Set API Key and custom API endpoint
        openai.api_key = 'XXX'
        openai.api_base = "XXX"  # your API key
        # Save conversation context
        self.messages = [
            {"role": "system", "content": f"Honeywords are decoy passwords used to detect unauthorized access. "
                                          f"Please generate honeywords similar to the target password to safeguard the database security."},
            {"role": "user",
             "content": f"Strong password patterns typically include non-repeating characters or complex combinations of letters and numbers."
             }
        ]

    def generate(self, original_password):
        recommended_passwords = recommend_similar_passwords_from_csv(
            original_password, 'sample dataset_hash.csv', num_recommendations=5
        )

        if not recommended_passwords:
            print("Unable to find enough similar passwords.")
            return None

        if self.test_mode:
            print("LSH recommended seed passwords:", [original_password] + recommended_passwords)

        passwords_str = ', '.join([f'({pwd})' for pwd in [original_password] + recommended_passwords])

        # Improved prompt
        final_prompt = (
            f"Here are six passwords, including the original password '{original_password}' "
            f"and five similar passwords: {passwords_str}. "
            "Please break down each password into smaller segments (e.g., substrings, individual characters), "
            "and creatively recombine these segments to form new passwords (honeywords) that look similar to the original. "
            "Ensure each honeyword is unique by varying the order, replacing characters, adding new segments, and avoiding repetitive structures or common prefixes. "
            "Ensure that the newly generated honeywords meet the following conditions:"
            "1. The length is between 6-18 characters; "
            "2. Contains at least two types of characters: uppercase letters, lowercase letters, numbers, and special symbols; "
            "3. The password cannot start with a special symbol. "
            "Generate exactly 20 different honeywords with diverse structures. "
            "Present the result **directly** in JSON format, with two fields: 'honeywords' (list of generated passwords) and 'explanation'."
        )

        honeywords_result = self.send_prompt(final_prompt, max_tokens=500)

        if honeywords_result:
            try:
                cleaned_result = honeywords_result.strip().replace("```json", "").replace("```", "")
                result_dict = json.loads(cleaned_result)

                # Filter valid honeywords and remove duplicates
                unique_honeywords = []
                seen_honeywords = set()

                for honeyword in result_dict["honeywords"]:
                    if honeyword not in seen_honeywords and self.is_valid_honeyword(honeyword):
                        unique_honeywords.append(honeyword)
                        seen_honeywords.add(honeyword)

                # Fill in any missing honeywords
                while len(unique_honeywords) < 20:
                    additional_honeyword = self.generate_additional_honeyword(original_password)
                    if additional_honeyword not in seen_honeywords and self.is_valid_honeyword(additional_honeyword):
                        unique_honeywords.append(additional_honeyword)
                        seen_honeywords.add(additional_honeyword)

                result_dict["honeywords"] = unique_honeywords[:20]
                return result_dict
            except json.JSONDecodeError as e:
                print(f"Error parsing the JSON result returned by LLM: {str(e)}")
                return self.generate_with_fallback(original_password)
        return self.generate_with_fallback(original_password)

    def is_valid_honeyword(self, honeyword):
        """
        Check if the honeyword meets length and character type requirements
        """
        if not (6 <= len(honeyword) <= 18):
            return False
        has_upper = any(c.isupper() for c in honeyword)
        has_lower = any(c.islower() for c in honeyword)
        has_digit = any(c.isdigit() for c in honeyword)
        return (has_upper + has_lower + has_digit) >= 2 and not honeyword[0] in "!@#$%^&*()-_=+[{]}|;:'\",<.>/?"

    def send_prompt(self, prompt, max_tokens=200):
        """
        Send a prompt to OpenAI's GPT model and return the response.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "You are a Cyberspace Security Expert."},
                          {"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.6
            )
            reply = response['choices'][0]['message']['content'].strip()
            if self.test_mode:
                #print(f"LLM reply: {reply}")
                pass
            return reply
        except Exception as e:
            print(f"Error during GPT call: {e}")
            return None

    def generate_additional_honeyword(self, original_password):
        """
        Fallback method to generate honeywords: replace the last 1-3 characters of the original password
        with random characters.
        """
        import random
        import string

        num_random_chars = random.randint(1, 3)
        random_chars = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=num_random_chars))
        return original_password[:-num_random_chars] + random_chars

    def generate_with_fallback(self, original_password):
        """
        Fallback method when GPT fails to generate honeywords or if an error occurs.
        """
        print("Using fallback method to generate honeywords.")
        honeywords = []
        for i in range(20):
            honeyword = self.generate_additional_honeyword(original_password)
            honeywords.append(honeyword)
        return {"honeywords": honeywords, "explanation": "Fallback method was used to generate honeywords."}

# Example usage
if __name__ == "__main__":
    generator = StrongPasswordGenerator("Peking University", test_mode=True)

    original_password = "DavidLermajr.4894"

    # Generate honeywords and print the LSH recommended seed data in test mode
    result = generator.generate(original_password)

    if result:
        honeywords = result.get("honeywords", [])
        explanation = result.get("explanation", "")

        # Print honeywords with 4 per line
        for i in range(0, len(honeywords), 4):
            print(", ".join(honeywords[i:i+4]))  # Print 4 honeywords per line

        # Print the final explanation
        print(f"\nExplanation: {explanation}")
