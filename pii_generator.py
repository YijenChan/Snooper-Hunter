import openai
import json
import random
import string

# Set API Key and custom API endpoint
openai.api_key = 'XXX'
openai.api_base = "XXX"  #your API key

class PIIGenerator:
    def __init__(self, test_mode=False):
        # Save conversation context
        self.messages = [
            {"role": "system", "content": f"Honeywords are decoy passwords used to detect unauthorized access. "
                                          f"Please generate honeywords similar to the target password to safeguard the database security."},
            {"role": "user",
             "content": f"PII-based password refers to the possibility that users may use their PII information (such as username, birthday, name, email) to construct their password. For example, a user with the name Luo Wei may create passwords for luowei123 or lw1234 (This has nothing to do with the actual data that follows)."
                        f"I will provide records with passwords and PII including username, birthday, name, email. "
                        f"Here are the recommended strategies: First, cut the password semantically and randomly select a substring. Then, randomly select one PII item (email only captures the part before @). Merge the substring and the selected PII in various orders. Lastly, add a random string of length 1-2 after honeywords with a very low probability."
             }
        ]

    def send_message_to_gpt(self, message):
        """
        Send a message to GPT and get a reply, while maintaining the conversation context.
        """
        # Append the user's message to the conversation
        self.messages.append({"role": "user", "content": message})

        try:
            # Call GPT API
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=self.messages,
                max_tokens=300,  # Limit the maximum number of generated tokens
                temperature=0.6
            )

            # Get the GPT reply
            reply = response['choices'][0]['message']['content'].strip()

            # Save GPT's reply to the context
            self.messages.append({"role": "assistant", "content": reply})

            return reply

        except Exception as e:
            print(f"Error calling GPT API: {str(e)}")
            return None

    def generate(self, password, username, birthday, name, email):
        """
        Accept a password and generate honeywords with a similar structure.
        """
        # Step 1: Send instruction to split the password and diversify PII information, with length limit
        init_instruction = (
            f"Now, I will give you a real instance. Please generate honeywords based on the input [({password}, {username}, {birthday}, {name}, {email})]."
            f" Follow this strategy closely: First, try splitting the password into multiple possible substrings (for example, '{password}' can be split into segments like 'cyl', 'ample', '0406')."
            f" Next, choose one PII value at random from [username, birthday, name, email (only before @)]."
            f" Then, combine these elements in diverse ways, for example by placing the PII before, after, or within the password segments."
            f" Limit each honeyword to a length of 6-12 characters to keep it similar to the target password in length. Finally, add a random 1-2 character suffix with low probability if it does not exceed the length limit. Make each honeyword unique and as indistinguishable from a real password as possible.")

        self.send_message_to_gpt(init_instruction)

        # Step 2: Provide final instruction with constraints and request the result in JSON format
        final_instruction = (f"Ensure that the newly generated honeywords meet the following conditions: "
                             f"1. The length is between 6-18 characters; "
                             f"2. Contains at least two types of characters: uppercase letters, lowercase letters, numbers and special symbols; "
                             f"3. The new password cannot start with a special symbol or number; "
                             f"Generate 20 unique honeywords with diverse structures and length from the given content, ensuring they are similar to the target password. Present the result **directly** in JSON format, with two fields: 'honeywords' (list of generated passwords) and 'explanation'.")

        # Pass the password and generate honeywords
        honeywords_response = self.send_message_to_gpt(final_instruction)

        # Clean up returned data, remove Markdown code block markers
        if honeywords_response:
            honeywords_response = honeywords_response.replace("```json", "").replace("```", "").strip()

        # Parse the returned JSON data
        try:
            honeywords_result = json.loads(honeywords_response)
            unique_honeywords = list(set([hw for hw in honeywords_result["honeywords"] if 6 <= len(hw) <= 12]))

            # Add local variations to generate more honeywords
            while len(unique_honeywords) < 20:
                modified_honeyword = self.modify_honeyword(random.choice(unique_honeywords))
                if modified_honeyword not in unique_honeywords:
                    unique_honeywords.append(modified_honeyword)

            return {"honeywords": unique_honeywords, "explanation": honeywords_result["explanation"]}

        except json.JSONDecodeError:
            print("Error parsing GPT's returned JSON, using fallback method to generate honeywords...")

            # Fallback method: Replace 1-3 random characters at the end of the password with random characters
            fallback_honeywords = []
            for i in range(20):
                honeyword = password[:-random.randint(1, 3)] + ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=random.randint(1, 3)))
                if honeyword not in fallback_honeywords:
                    fallback_honeywords.append(honeyword)

            return {"honeywords": fallback_honeywords, "explanation": "Fallback method used due to error in GPT response."}

    def modify_honeyword(self, honeyword):
        """
        Modify a honeyword by appending a random character or altering it slightly.
        """
        return honeyword + random.choice(string.ascii_letters + string.digits)

# Test the PIIGenerator class
if __name__ == "__main__":
    generator = PIIGenerator()
    password = "zs123a"
    username = "supercat"
    birthday = "1999-05-02"
    name = "zhangsan"
    email = "hao123@example.com"
    result = generator.generate(password, username, birthday, name, email)

    if result:
        honeywords = result.get("honeywords", [])
        explanation = result.get("explanation", "")

        # Print 4 honeywords per line
        for i in range(0, len(honeywords), 4):
            print(", ".join(honeywords[i:i + 4]))  # Print 4 honeywords per line

        # Print the explanation
        print(f"\nExplanation: {explanation}")
