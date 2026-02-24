# -------- Base Image --------
FROM python:3.11-slim

# -------- Environment --------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -------- System Dependencies --------
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# -------- Working Directory --------
WORKDIR /app

# -------- Install Python Dependencies --------
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# -------- Copy Project --------
COPY . .

# -------- Create Required Folders --------
RUN mkdir -p logs uploads backups

# -------- Expose Port --------
EXPOSE 5000

# -------- Run Application --------
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]