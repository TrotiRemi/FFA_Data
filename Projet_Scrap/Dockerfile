FROM python:3.12.6 

WORKDIR /app
COPY . /app/
RUN pip install -r requirements.txt
CMD cd FFA && scrapy crawl FFA1 -o Test123.csv && cd .. && cp FFA/Test123.csv . && python Test.py 