FROM python:alpine3.18
WORKDIR /app
#RUN apk add nano
RUN apk add tzdata
COPY ./app .
RUN pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt
CMD [ "python", "/app/nutcase.py" ]
