FROM node:22-bookworm-slim
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY app.js review.js dealership.js ./
COPY data/ ./data/
EXPOSE 3030
CMD ["node", "app.js"]
