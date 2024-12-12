from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, from_unixtime, split,  col, from_json, coalesce, lit,  lower, trim
from pyspark.sql.types import StructType
from resources.kafka_connector import KafkaConnector
import json

def main():
  spark = SparkSession \
      .builder \
      .appName("user_login_clean") \
      .getOrCreate()

  # Load configuration variables
  with open("/opt/spark-apps/data_processing/config.json", "r") as config_file:
    config = json.load(config_file)['user_login_clean']
    bootstrap_server = config['bootstrap_server']
    topic_in = config['topic_in']
    topic_out = config['topic_out']
    schema_location = config['schema_location']
    checkpoint_location = config['checkpoint_location']

  # Load the JSON schema from file
  with open(schema_location, "r") as schema_file:
    schema_json = json.load(schema_file)
    spark_schema = StructType.fromJson(schema_json)

  kafka_con = KafkaConnector(bootstrap_server, spark)

  print(f"Reading raw data from kafka topic {topic_in}")
  df = kafka_con.read_stream_to_df(topic_in, spark_schema)


  # Apply cleaning transformations
  df = (
      df.withColumn("timestamp", from_unixtime(col("timestamp")).cast("timestamp"))
              .withColumn("locale", coalesce(col("locale"), lit("UNK")))
              .withColumn("device_type", lower(trim(col("device_type"))))
  )

  print(f"Writing to kafka topic {topic_out}")
  query = kafka_con.write_stream_df_to_topic(df=df, 
                                            topic=topic_out, 
                                            mode="append", 
                                            checkpoint_location=checkpoint_location)
  query.awaitTermination()

if __name__ == "__main__":
  main()