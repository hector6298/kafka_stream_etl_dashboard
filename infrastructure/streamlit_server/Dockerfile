FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install kafka-python streamlit plotly pandas

# Copy your application code
COPY --from=streamlit_app visualization /visualization

# Set the working directory
WORKDIR /visualization

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "user_login_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]