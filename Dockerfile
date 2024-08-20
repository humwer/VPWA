FROM python:3.12-slim-bookworm
COPY . /app
WORKDIR /app
RUN rm -rf Dockerfile docker-compose.yml .Dockerfile.swp .git .gitignore README.md
RUN pip install -r requirements.txt
RUN chmod +x ./run.sh
CMD ["sh", "-c", "./run.sh"]
EXPOSE 6177