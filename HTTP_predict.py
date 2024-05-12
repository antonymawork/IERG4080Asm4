import io
import json
import redis
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import requests
from bs4 import BeautifulSoup
from newspaper import Article

REDIS_HOST = 'your-redis-instance-private-ip-or-public-dns'
REDIS_PORT = 6379
REDIS_DB = 0

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

tokenizer = AutoTokenizer.from_pretrained("AyoubChLin/Bart-MNLI-CNN_news")
model = AutoModelForSequenceClassification.from_pretrained("AyoubChLin/Bart-MNLI-CNN_news")
classifier = pipeline(
    "zero-shot-classification",
    model=model,
    tokenizer=tokenizer,
    device=0
)

def extract_text_from_url(url, max_retries=5):
    """Extract main text content from the given URL with auto-retry."""
    retry_count = 0
    while retry_count < max_retries:
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            if article.text:
                return article.text
            else:
                print(f"Could not extract main content from the URL: {url}")
                retry_count += 1
        except Exception as e:
            print(f"Error fetching content from URL: {e}")
            retry_count += 1
        
    print(f"Failed to extract text from the URL after {max_retries} retries.")
    return None

def generate_predictions(text):
    """Generate predictions using the model for the given text."""
    candidate_labels = ["sports", "finance", "technology", "science"]
    predictions = classifier(text, candidate_labels, multi_class=True)
    return predictions

def continuously_receive_messages():
    while True:
        try:
            print("Waiting for news article URL...")
            _, message = r.brpop("download")
            data = json.loads(message)
            print(f"Received message for processing: {data}")

            url = data["url"]
            task_id = data["task_id"]
            timestamp = data["timestamp"]
            print(f"Processing news article from URL: {url}")

            text = extract_text_from_url(url)
            if text is not None:
                predictions = generate_predictions(text)
                result_message = {
                    "task_id": task_id,
                    "timestamp": timestamp,
                    "url": url,
                    "predictions": predictions
                }
                print(f"Generated result_message: {result_message}")
                r.lpush("prediction", json.dumps(result_message))
            else:
                print("Failed to extract text from the URL.")
        except Exception as e:
            print(f"An error occurred during message processing: {e}")

if __name__ == "__main__":
    continuously_receive_messages()