import os
import json
import sqlite3
from datetime import datetime
from groq import Groq
from instagrapi import Client as InstaClient

class AIGirlfriendBot:
    def __init__(self, username, password, groq_api_key):
        self.username = username
        self.groq = Groq(api_key=groq_api_key)
        self.client = InstaClient()
        self.db = sqlite3.connect('conversations.db')
        self._init_db()
        self._login(username, password)
        
        self.personality = "Reply in 5-10 words max. Be flirty, cute, use emojis."

    def _init_db(self):
        cursor = self.db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS chats
                         (user_id TEXT, username TEXT, message TEXT, 
                          response TEXT, timestamp TEXT)''')
        self.db.commit()

    def _login(self, username, password):
        session_file = f"{username}_session.json"
        
        if os.path.exists(session_file):
            try:
                self.client.load_settings(session_file)
                self.client.login(username, password)
                print("Logged in using saved session")
                return
            except:
                os.remove(session_file)
        
        self.client.delay_range = [2, 5]
        self.client.set_device({
            "app_version": "269.0.0.18.75",
            "android_version": 26,
            "android_release": "8.0.0",
            "dpi": "480dpi",
            "resolution": "1080x1920",
            "manufacturer": "OnePlus",
            "device": "OnePlus6T",
            "model": "ONEPLUS A6003",
            "cpu": "qcom",
            "version_code": "314665256"
        })
        
        import time
        time.sleep(3)
        
        try:
            self.client.login(username, password)
            self.client.dump_settings(session_file)
            print("Logged in successfully")
        except Exception as e:
            error_msg = str(e)
            if "challenge_required" in error_msg:
                print("Instagram requires verification. Check your Instagram app/email.")
                code = input("Enter verification code: ")
                self.client.challenge_code_handler(username, code)
                self.client.dump_settings(session_file)
            elif "two_factor" in error_msg:
                code = input("Enter 2FA code: ")
                self.client.two_factor_login(code)
                self.client.dump_settings(session_file)
            else:
                print(f"\n❌ Instagram Login Blocked")
                print("\nQuick Fix:")
                print("1. Open Instagram app on your phone")
                print("2. Login with this account")
                print("3. Wait 5 minutes")
                print("4. Run the bot again")
                print("\nOR use a fresh Instagram account created from this device/network")
                import sys
                sys.exit(1)

    def get_chat_history(self, user_id, limit=20):
        cursor = self.db.cursor()
        cursor.execute('''SELECT message, response FROM chats 
                         WHERE user_id=? ORDER BY timestamp DESC LIMIT ?''',
                       (user_id, limit))
        return cursor.fetchall()[::-1]

    def save_chat(self, user_id, username, message, response):
        cursor = self.db.cursor()
        cursor.execute('''INSERT INTO chats VALUES (?, ?, ?, ?, ?)''',
                      (user_id, username, message, response, 
                       datetime.now().isoformat()))
        self.db.commit()

    def generate_response(self, user_id, message):
        history = self.get_chat_history(user_id)
        messages = [{"role": "system", "content": self.personality}]
        
        for msg, resp in history:
            messages.append({"role": "user", "content": msg})
            messages.append({"role": "assistant", "content": resp})
        
        messages.append({"role": "user", "content": message})
        
        try:
            response = self.groq.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=1.0,
                max_tokens=20
            )
            return response.choices[0].message.content
        except:
            return "Hey! 💕"

    def handle_dms(self):
        threads = self.client.direct_threads(amount=20)
        
        for thread in threads:
            messages = self.client.direct_messages(thread.id, amount=1)
            if not messages:
                continue
                
            last_msg = messages[0]
            if last_msg.user_id == self.client.user_id:
                continue
            
            user_id = str(last_msg.user_id)
            username = thread.users[0].username
            message_text = last_msg.text
            
            if not message_text:
                continue
            
            response = self.generate_response(user_id, message_text)
            self.save_chat(user_id, username, message_text, response)
            self.client.direct_send(response, thread_ids=[thread.id])
            print(f"Replied to {username}: {response[:50]}...")

    def post_content(self, image_path, caption):
        self.client.photo_upload(image_path, caption)
        print(f"Posted: {caption[:50]}...")

    def run(self, check_interval=0.5):
        import time
        print("AI Girlfriend Bot started...")
        while True:
            try:
                self.handle_dms()
                time.sleep(check_interval)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(check_interval)

if __name__ == "__main__":
    bot = AIGirlfriendBot(
        username=os.getenv("INSTAGRAM_USERNAME"),
        password=os.getenv("INSTAGRAM_PASSWORD"),
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    bot.run()
