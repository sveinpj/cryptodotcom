FROM python:3.9.18
COPY requirements.txt /tmp/
RUN apt-get update
RUN pip install -r /tmp/requirements.txt
CMD ["python", "/tmp/crypto.py"]
