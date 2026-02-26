import pandas as pd
import requests
from playwright.sync_api import sync_playwright
from pathlib import Path
import time

class NewsCracker:
    def __init__(self, model_name="gemma2:2b"):
        self.model_name = model_name
        self.results = []

    def get_content(self, google_url):
        with sync_playwright() as p:
            print(f" Resolving: {google_url[:60]}...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})
            
            try:

                page.goto(google_url, wait_until="networkidle", timeout=60000)
                page.wait_for_load_state("domcontentloaded")
                
                final_url = page.url
                title = page.title()
              
                paragraphs = page.locator("p").all_inner_texts()
                clean_text = "\n".join([p for p in paragraphs if len(p) > 60])
                
                browser.close()
                return {"title": title, "url": final_url, "text": clean_text} if len(clean_text) > 200 else None
                
            except Exception as e:
                print(f"Browser Error: {e}")
                browser.close()
                return None

    def summarize(self, text):
        print(" Gemma2 is summarizing...")
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": f"Provide a 3-bullet point summary of this article:\n\n{text[:4000]}",
                    "stream": False
                }
            )
            return response.json().get('response', 'Summary missing')
        except:
            return "Ollama connection failed."

    def process_file(self, file_name):
  
        df_input = pd.read_csv(file_name)
        print(f"Found {len(df_input)} articles in {file_name}")

        for index, row in df_input.iterrows():
            print(f"\n--- Processing Article {index + 1} ---")
            data = self.get_content(row['link'])
            
            if data:
                summary = self.summarize(data['text'])
                self.results.append({
                    "Date": row['published'],
                    "Original_Title": row['title'],
                    "Source_URL": data['url'],
                    "Summary": summary
                })
            
                pd.DataFrame(self.results).to_csv("TCS_Final_Analysis.csv", index=False)
            else:
                print(" Skipping: Could not extract full text.")
            
            time.sleep(1) 

if __name__ == "__main__":
    bot = NewsCracker()

    bot.process_file("TCS_25April2025_fullnews.csv")