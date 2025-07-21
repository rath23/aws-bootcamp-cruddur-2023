# FROM node:16.18

# ENV PORT=3000

# COPY . /frontend-react-js
# WORKDIR /frontend-react-js
# RUN npm install
# EXPOSE ${PORT}
# CMD ["npm", "start"]

# ──────────────────────────────────────────────
# Stage 1: Build React App
FROM node:16.18 AS builder

WORKDIR /app

# Copy only package files first for better caching
COPY package*.json ./
RUN npm install

# Copy rest of your app and build
COPY . .
ARG REACT_APP_BACKEND_URL
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL
RUN npm run build

# ──────────────────────────────────────────────
# Stage 2: Serve the build (use `serve`)
FROM node:16.18

WORKDIR /app

# Install a static file server
RUN npm install -g serve

# Copy built files from builder stage
COPY --from=builder /app/build ./build

# Default port
ENV PORT=3000

EXPOSE ${PORT}
CMD ["serve", "-s", "build", "-l", "3000"]
