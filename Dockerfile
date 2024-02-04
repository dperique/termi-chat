FROM python:3.8-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "./python/termi-chat.py"]

# Do this to allow user to pass arguments to the entrypoint
CMD ["--help"]