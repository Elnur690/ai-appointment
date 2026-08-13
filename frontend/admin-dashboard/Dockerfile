FROM node:20-alpine AS development

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 22300

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "22300"]
