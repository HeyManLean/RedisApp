FROM python:3.7

ADD . /data

WORKDIR /data

RUN pip install -i https://pypi.douban.com/simple/ pipenv && pipenv install

# ENTRYPOINT [ "python", "app.py" ]
CMD ["pipenv", "run", "python", "app.py"]