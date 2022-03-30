FROM python:3.10.0

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install fastapi uvicorn pydantic

COPY ./main.py /code/
#EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]