from flask import Flask, request, jsonify, redirect, url_for
import json
import redis
import uuid
from datetime import datetime

# Initialize the Flask application
app = Flask(__name__)

# Create Redis connection
r = redis.Redis()

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Submit News Article URL</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100">
        <div class="max-w-lg mx-auto mt-8">
            <h2 class="text-2xl font-bold mb-4">Submit News Article URL for Classification</h2>
            <form action="/process" method="post" class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
                <div class="mb-4">
                    <label for="url" class="block text-gray-700 text-sm font-bold mb-2">News Article URL:</label>
                    <input type="text" id="url" name="url" placeholder="Enter News Article URL here" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                </div>
                <div class="flex items-center justify-between">
                    <input type="submit" value="Submit" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                </div>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/process', methods=['POST'])
def process_request():
    task_id = str(uuid.uuid4())
    if 'url' in request.form:
        url = request.form['url']
        message = {
            "task_id": task_id,
            "timestamp": str(datetime.now()),
            "url": url
        }
        print(f"Pushing to Redis: {message}")
        r.lpush("download", json.dumps(message))
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Processing News Article</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            var taskId = "{task_id}";
            function checkResult() {{
                var xhr = new XMLHttpRequest();
                xhr.open("GET", "/result/" + taskId, true);
                xhr.onload = function () {{
                    if (xhr.status === 200) {{
                        var response = JSON.parse(xhr.responseText);
                        if ('result' in response) {{
                            var predictions = JSON.parse(response.result).predictions;
                            var tableHtml = '<table class="table-auto w-full text-left whitespace-no-wrap bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">';
                            tableHtml += '<thead><tr><th class="px-4 py-3 title-font tracking-wider font-medium text-gray-900 text-sm bg-gray-100 rounded-tl rounded-bl">Category</th><th class="px-4 py-3 title-font tracking-wider font-medium text-gray-900 text-sm bg-gray-100">Probability</th></tr></thead>';
                            tableHtml += '<tbody>';
                            for (var i = 0; i < predictions.labels.length; i++) {{
                                tableHtml += '<tr><td class="px-4 py-3 text-lg font-bold">' + predictions.labels[i] + '</td><td class="px-4 py-3 text-lg font-bold">' + (predictions.scores[i] * 100).toFixed(2) + '%</td></tr>';
                            }}
                            tableHtml += '</tbody></table>';
                            document.getElementById('status').innerHTML = tableHtml;
                            clearInterval(intervalId);
                        }} else {{
                            document.getElementById('status').innerHTML = 'Processing...';
                        }}
                    }} else if (xhr.status === 202) {{
                        document.getElementById('status').innerHTML = 'Processing...';
                    }} else {{
                        document.getElementById('status').innerHTML = 'Error fetching result.';
                    }}
                }};
                xhr.send();
            }}
            var intervalId = setInterval(checkResult, 2000); // Check every 2 seconds
        </script>
    </head>
    <body class="bg-gray-100">
        <div class="max-w-lg mx-auto mt-8">
            <h2 class="text-2xl font-bold mb-4">News Article Classification Result</h2>
            <p id="status" class="text-lg">Processing...</p>
        </div>
    </body>
    </html>
    '''

@app.route('/result/<task_id>', methods=['GET'])
def get_result(task_id):
    result = r.get(f"result:{task_id}")
    if result:
        return jsonify({"result": result.decode('utf-8')}), 200
    else:
        return jsonify({"error": "Error"}), 202

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
