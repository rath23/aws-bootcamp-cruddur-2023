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
FROM python:3.10-slim-buster AS builder

WORKDIR /app

# Copy only requirements to install dependencies
COPY requirements.txt .

# Install to a custom folder to prevent installing cache into final image
RUN pip install --user -r requirements.txt

# ───────────────────────────────────────────────────────────
# Stage 2: Runtime Stage — minimal, production-ready image
FROM python:3.10-slim-buster

WORKDIR /app

# Copy just the dependencies from builder
COPY --from=builder /root/.local /root/.local

# Add app source code
COPY . .

# Ensure the user-installed packages are found
ENV PATH=/root/.local/bin:$PATH

ENV FLASK_ENV=development
EXPOSE ${PORT}

CMD ["flask", "run", "--host=0.0.0.0", "--port=4567"]
