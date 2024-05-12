import threading
import json
import redis

# Create Redis connection
REDIS_HOST = '52.72.49.114'
REDIS_PORT = 6379
REDIS_DB = 0

r = redis.Redis(host=REDIS_HOST, 
            port=REDIS_PORT, 
            db=REDIS_DB, 
            password=4080, 
            health_check_interval=10,
            socket_timeout=10, socket_keepalive=True,
            socket_connect_timeout=10, retry_on_timeout=True
            )

def listen_predictions():
    """Continuously listen for and process prediction tasks, printing detailed results."""
    while True:
        _, message = r.blpop("prediction")
        print(f"Received message from Redis: {message}")
        task = json.loads(message)
        print(f"Received task: {task}")
        task_id = task.get("task_id")
        redis_key = f"result:{task_id}"
        redis_value = json.dumps(task)
        r.set(redis_key, redis_value)
        
        # Handle the prediction results
        predictions = task['predictions']
        print("News Article Classification Results:")
        for label, score in zip(predictions['labels'], predictions['scores']):
            print(f"Label: {label}, Score: {score:.4f}")

def perform_prediction(task):
    """Simulates prediction logic and returns the task data unchanged."""
    return task

if __name__ == "__main__":
    prediction_thread = threading.Thread(target=listen_predictions)
    prediction_thread.start()
