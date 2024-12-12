from pyspark.sql import SparkSession
from pyspark.sql.functions import  window, approx_count_distinct, hash
from pyspark.sql.types import StructType
from resources.kafka_connector import KafkaConnector
import json

def main():
  spark = SparkSession \
      .builder \
      .appName("user_login_stats") \
      .getOrCreate()


  # Load configuration variables
  with open("/opt/spark-apps/data_processing/config.json", "r") as config_file:
    config = json.load(config_file)['user_login_stats']
    bootstrap_server = config['bootstrap_server']
    topic_in = config['topic_in']
    topic_out = config['topic_out']
    schema_location = config['schema_location']
    checkpoint_location = config['checkpoint_location']
    window_duration = config['window_duration']
    slide_duration = config['slide_duration']
    watermark_duration = config['watermark_duration']

  # Load the YAML schema from the file
  with open(schema_location, 'r') as yaml_file:
      schema_yaml = json.load(yaml_file)
      spark_schema = StructType.fromJson(schema_yaml)

  # Reading from topic
  kafka_con = KafkaConnector(bootstrap_server, spark)

  print(f"Reading processed data from kafka topic {topic_in}")
  df = kafka_con.read_stream_to_df(topic_in, spark_schema)

  # Calculate aggregations
  df = df.withWatermark("timestamp", watermark_duration) \
      .groupBy(window("timestamp", window_duration, slide_duration).alias("window"), \
              "locale") \
      .agg(
          approx_count_distinct("user_id").alias("unique_users"),
          approx_count_distinct("device_id").alias("distinct_devices")
      )
  
  print(df.columns)
  df = df.withColumn("key", hash("window", "locale"))

  print(f"Writing to kafka topic {topic_out}")
  query = kafka_con.write_stream_df_to_topic(df=df, 
                                            topic=topic_out, 
                                            mode="append", 
                                            checkpoint_location=checkpoint_location)
  query.awaitTermination()


if __name__ == "__main__":
  main()
