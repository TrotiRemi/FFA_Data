FROM python:3.12.6 

WORKDIR /app
COPY . /app/
RUN pip install -r requirements.txt
CMD cd FFA && scrapy crawl Extract_Course.py -o Course.csv && cd .. && cp FFA/Course.csv . && python Extract_Coureur.py && python Lavage.py 