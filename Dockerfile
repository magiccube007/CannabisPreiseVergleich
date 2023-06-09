FROM python:3.9

RUN pip install --upgrade pip

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

RUN mkdir /app
COPY ./ /app

WORKDIR /app

CMD ["python", "telegrammbot.py"]
