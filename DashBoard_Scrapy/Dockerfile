FROM python:3.12.6

WORKDIR /app
COPY . /app/
RUN pip install -r requirements.txt

# Copie et donne les permissions au script d'attente
COPY wait_for_file.sh /app/wait_for_file.sh
RUN chmod +x /app/wait_for_file.sh

CMD ["./wait_for_file.sh", "python", "main.py"]
