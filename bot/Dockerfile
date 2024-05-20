FROM python:3.11-slim
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY bot.py app.py
CMD ["python", "app.py"]