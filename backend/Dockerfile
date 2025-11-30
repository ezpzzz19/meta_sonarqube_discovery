FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    git \
    curl \
    wget \
    unzip \
    openjdk-21-jdk-headless \
    && rm -rf /var/lib/apt/lists/*

# Install SonarQube Scanner (Architecture-aware)
# This version is pure Java and works on both x86 and ARM
RUN SCANNER_VERSION=5.0.1.3006 && \
    ARCH=$(dpkg --print-architecture) && \
    echo "Building for architecture: $ARCH" && \
    wget -q https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${SCANNER_VERSION}.zip -O /tmp/sonar-scanner.zip && \
    unzip -q /tmp/sonar-scanner.zip -d /opt && \
    mv /opt/sonar-scanner-${SCANNER_VERSION} /opt/sonar-scanner && \
    chmod +x /opt/sonar-scanner/bin/sonar-scanner && \
    ln -s /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner && \
    rm /tmp/sonar-scanner.zip && \
    sonar-scanner --version || echo "Scanner installed"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make scan script executable
RUN chmod +x scan_repo.sh

# Run migrations and start server
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
