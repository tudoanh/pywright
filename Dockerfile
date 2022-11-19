FROM mcr.microsoft.com/playwright/python:v1.28.0-focal

WORKDIR /root

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY ./entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./api_server.py ./api_server.py
COPY ./templates ./templates

EXPOSE 5000

ENTRYPOINT [ "/entrypoint" ]
