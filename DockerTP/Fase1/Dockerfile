FROM python:3.10-slim

WORKDIR /app

# Instala apenas as duas ferramentas vitais para a Web da Fase 1
RUN pip install --no-cache-dir flask flask-session

COPY . /app

# Por defeito, arranca a Web. (O compose vai forçar o DataServer.py no contentor 2)
CMD ["python", "Server.py"]