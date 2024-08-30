FROM python:3.10

WORKDIR /app

ENV TZ=Asia/Shanghai

COPY requirements.txt .

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD gunicorn -c gunicorn.conf.py src.main:app
