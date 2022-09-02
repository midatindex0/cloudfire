FROM python:3.8

ADD . ./

RUN pip install -r requirements.txt
RUN playwright install firefox
RUN playwright install-deps

EXPOSE ${PORT}

CMD ["uvicorn", "main:app"]