FROM python:3.11-slim

WORKDIR /app

RUN useradd -m -u 1000 ctfuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python generate_logs.py && chown -R ctfuser:ctfuser /app

USER ctfuser

EXPOSE 5005

ENV PORT=5005
ENV STAGE6_HOST=stage6
ENV STAGE6_PORT=22
ENV STAGE6_WEB_URL=http://stage6:5006

CMD ["python", "app.py"]
