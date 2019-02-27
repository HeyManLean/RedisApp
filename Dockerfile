FROM python:3.6

ADD . /data

WORKDIR /data

RUN pip install -r requirements.txt

# ENTRYPOINT [ "python3 app.py" ]
CMD ["python", "app.py"]