
# News Classification with Machine Learning

This repository contains code for classifying news articles into various topics using machine learning. The project supports execution both locally and on AWS instances.

## Running Locally

To run the application on your local machine, follow these steps:

1. **Download the Required Files**:
   - `predictionWorker_local.py`
   - `resultProcessor_local.py`
   - `server_local.py`

2. **Install Redis**:
   - Install Redis on your local machine based on your operating system.
   - Ensure that Redis is running.

3. **Install Required Python Packages**:
   ```bash
   pip install redis transformers requests torch newspaper3k bs4 lxml_html_clean
   ```

4. **Run the Application**:
   - Open three separate terminals:
     - In the first terminal, run:
       ```bash
       python predictionWorker_local.py
       ```
     - In the second terminal, run:
       ```bash
       python resultProcessor_local.py
       ```
     - In the third terminal, run:
       ```bash
       python server_local.py
       ```

5. **Access the Application**:
   - Open a web browser and navigate to `127.0.0.1:5000`.
   - Enter a URL of an online article/news, fill in the field, and click submit.
   - The application will display the probability of each category (sports, finance, technology, science).

## Running on AWS

To run the application on AWS, follow these steps:

### AWS EC2 Structure

1. **Redis Instance**:
   - Create a `t2.micro` EC2 instance.
   - Associate an Elastic IP to it.
   - Set Security Group to accept traffic on ports 80, 443, 6379, 5000, or all traffic (for testing).

2. **Install Redis**:
   ```bash
   sudo apt update
   sudo apt install redis-server
   sudo nano /etc/redis/redis.conf
   ```
   - Replace `bind 127.0.0.1 -::1` with `bind 0.0.0.0`.
   - Replace `# requirepass foobared` with `requirepass 4080`.
   ```bash
   sudo systemctl restart redis-server
   ```

3. **Prediction Worker Instance**:
   - Create a `t2.large` EC2 instance.
   - Install required packages:
     ```bash
     sudo apt update
     sudo apt install python3 python3-pip python3-venv
     python3 -m venv article2topic
     source article2topic/bin/activate
     pip install redis transformers requests torch newspaper3k bs4 lxml_html_clean
     ```
   - Download the source code into a folder named `IERG4080Asm4`.
   - Update `HTTP_predict.py` with your Redis instance's Elastic IP.
   - Run the prediction worker:
     ```bash
     python3 HTTP_predict.py
     ```

4. **Result Processor Instance**:
   - Create a `t2.micro` EC2 instance.
   - Install required packages:
     ```bash
     sudo apt update
     sudo apt install python3 python3-pip python3-venv
     python3 -m venv article2topic
     source article2topic/bin/activate
     pip install redis requests
     ```
   - Download the source code into a folder named `IERG4080Asm4`.
   - Update `HTTP_main.py` with your Redis instance's Elastic IP.
   - Run the result processor:
     ```bash
     python3 HTTP_main.py
     ```

5. **Web Server Instance**:
   - Create a `t2.micro` EC2 instance.
   - Associate an Elastic IP to it.
   - Set Security Group for the instance (you can use the previously set security group).
   - Install required packages:
     ```bash
     sudo apt update
     sudo apt install python3 python3-pip python3-venv
     python3 -m venv article2topic
     source article2topic/bin/activate
     pip install flask redis requests
     ```
   - Download the source code into a folder named `IERG4080Asm4`.
   - Update `server.py` with your Redis instance's Elastic IP.
   - Run the web server:
     ```bash
     python3 server.py
     ```

### Access the Application

- Navigate to `{Web Server Instance's Elastic IP}:5000` in your browser.
- Enter a URL of an online article/news, fill in the field, and click submit.
- The application will display the probability of each category (sports, finance, technology, science).

## Reference

- Model used: [AyoubChLin/Bart-MNLI-CNN_news](https://huggingface.co/AyoubChLin/Bart-MNLI-CNN_news)
