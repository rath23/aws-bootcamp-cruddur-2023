# FROM python:3.10-slim-buster

# WORKDIR /backend-flask

# COPY requirements.txt requirements.txt
# RUN pip3 install -r requirements.txt

# COPY . .

# ENV FLASK_ENV=development

# EXPOSE ${PORT}
# CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567"]

# ───────────────────────────────────────────────────────────
# Stage 1: Builder Stage — installs dependencies
FROM 651746472793.dkr.ecr.ap-south-1.amazonaws.com/cruddur-python:3.10-slim-buster AS builder


WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# ───────────────────────────────────────────────────────────
# Stage 2: Runtime Stage — minimal, production-ready image
FROM 651746472793.dkr.ecr.ap-south-1.amazonaws.com/cruddur-python:3.10-slim-buster


WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
ENV PORT=4567
EXPOSE 4567

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:4567", "app:app"]
