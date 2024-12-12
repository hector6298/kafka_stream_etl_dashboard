#!/bin/bash

echo "### Setting Up Infrastructure ###"

# Create or clean the data_lake folder
echo "Setting up data_lake folder..."
if [ -d "./data_lake" ]; then
    echo "data_lake folder exists. Removing its contents..."
    rm -rf ./data_lake/*
else
    echo "data_lake folder does not exist. Creating it..."
    mkdir ./data_lake
fi

echo "Navigating to app/resources folder..."
cd app/ || exit

echo "Zipping resources folder..."
zip -r resources.zip resources
cd ../ || exit

echo "Navigating to the infrastructure folder..."
cd infrastructure || exit

echo "Building the Spark cluster Docker image..."
cd spark_cluster || exit
docker build -t apache-spark:3.5.3 .
cd .. || exit

echo "Building the Streamlit server Docker image..."
cd streamlit_server || exit
docker build --build-context streamlit_app=../../app -t streamlit-server:1.0.0 .
cd .. || exit

echo "Starting infrastructure with Docker Compose..."
docker compose up -d

sleep 15

spark_master_container=$(docker ps --filter "name=spark-master" --format "{{.Names}}")

# Launching the first Spark job (data cleansing) in detached mode
echo "Submitting Spark job for cleaning..."
docker exec -d -it "$spark_master_container" /bin/sh -c "
/opt/spark/bin/spark-submit --name 'user_login_clean' \
    --master spark://spark-master:7077 \
    --py-files /opt/spark-apps/resources.zip \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3 \
    --total-executor-cores 1 \
    /opt/spark-apps/data_processing/user_login_clean.py
"

sleep 30

# Launching the second Spark job (window aggregations) in detached mode
echo "Submitting Spark job for aggregation..."
docker exec -d -it "$spark_master_container" /bin/sh -c "
/opt/spark/bin/spark-submit --name 'user_login_stats' \
    --master spark://spark-master:7077 \
    --py-files /opt/spark-apps/resources.zip \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3 \
    --total-executor-cores 1 \
    /opt/spark-apps/data_processing/user_login_stats.py
"

echo "### Infrastructure setup and Spark jobs submission completed! ###"
echo "
Please enter the following URLs on your browser:
- Spark UI: http://localhost:9090/
- Visualization Server: http://localhost:10501
"