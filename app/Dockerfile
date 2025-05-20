FROM python:3.12-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

# set the working directory
WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# copy the project files
COPY . .

# run django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]