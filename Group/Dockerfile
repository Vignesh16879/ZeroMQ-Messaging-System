FROM python:3.8

WORKDIR /app
ADD . /app

RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80
ENV NAME World

CMD ["python", "group.py"]