FROM python:3.11.7
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
ENV DB_HOST=db
ENV DB_USER=postgres
ENV DB_PASSWORD=22611971
ENV DB_NAME=hh_vacancies
CMD ["python", "hh_parser.py"]