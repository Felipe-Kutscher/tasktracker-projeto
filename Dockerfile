# Base leve do sistema (Python 3.11 em Debian slim)
FROM python:3.11-slim

# Pasta central de operações dentro do container
WORKDIR /app

# Logs/prints aparecem imediatamente no terminal (sem buffer)
ENV PYTHONUNBUFFERED=1

# Instala as dependências primeiro: o Docker reaproveita essa camada em cache
# enquanto o requirements.txt não mudar (rebuilds mais rápidos)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Injeta o código local no container
COPY src/ /app/src/

# Gatilho que dispara a execução da CLI
CMD ["python", "src/main.py"]
