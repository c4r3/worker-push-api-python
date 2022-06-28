FROM python:3.9

WORKDIR /opt/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
EXPOSE 8000

#CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
CMD ["python3", "main.py", "./config.ini"]
