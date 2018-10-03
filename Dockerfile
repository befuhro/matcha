FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY /app/requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt