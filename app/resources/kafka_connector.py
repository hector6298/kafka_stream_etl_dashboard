from pyspark.sql.types import StructType
from pyspark.sql.functions import col, from_json
from pyspark.sql import DataFrame

class KafkaConnector:
    """
    A utility class for integrating Kafka with Spark Structured Streaming.

    This class provides methods to read streaming data from Kafka topics
    into Spark DataFrames and to write Spark DataFrames back to Kafka topics.

    Attributes
    ----------
    _bootstrap_server : str
        The Kafka bootstrap server address.
    _spark : pyspark.sql.SparkSession
        The Spark session instance to use for streaming and data processing.
    """

    def __init__(self, bootstrap_server: str, spark):
        """
        Initialize the KafkaConnector.

        Parameters
        ----------
        bootstrap_server : str
            The Kafka bootstrap server address (e.g., "kafka:29092").
        spark : pyspark.sql.SparkSession
            The Spark session to use for reading and writing Kafka streams.
        """
        self._bootstrap_server = bootstrap_server
        self._spark = spark

    def read_stream_to_df(self, topic: str, spark_schema: StructType) -> DataFrame:
        """
        Read streaming data from a Kafka topic into a Spark DataFrame.

        Parameters
        ----------
        topic : str
            The name of the Kafka topic to subscribe to.
        spark_schema : pyspark.sql.types.StructType
            The schema of the data to parse from the Kafka topic's messages.

        Returns
        -------
        pyspark.sql.DataFrame
            A Spark DataFrame containing the parsed Kafka messages. The resulting
            DataFrame includes the following columns:
                - `key` : str
                    The Kafka message key.
                - Other columns based on the JSON structure of the Kafka message `value`.

        Examples
        --------
        >>> schema = StructType([
        ...     StructField("user_id", StringType(), True),
        ...     StructField("timestamp", TimestampType(), True)
        ... ])
        >>> connector = KafkaConnector("kafka:29092", spark)
        >>> df = connector.read_stream_to_df("topic_in", schema)
        """
        df = self._spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self._bootstrap_server) \
            .option("subscribe", topic) \
            .load()
        
        df = df.selectExpr("CAST(key AS STRING) as key", "CAST(value AS STRING) as value")
        return df.select([
            col("key"),
            from_json(col("value").cast("string"), spark_schema).alias("data")
        ]).select(["key", "data.*"])
    
    def write_stream_df_to_topic(self, 
                                 df: DataFrame, 
                                 topic: str, 
                                 mode: str,
                                 checkpoint_location: str):
        """
        Write a Spark DataFrame to a Kafka topic as a streaming job.

        Parameters
        ----------
        df : pyspark.sql.DataFrame
            The Spark DataFrame to write to Kafka. The DataFrame must include a 
            `key` column and other columns to serialize into the Kafka message `value`.
        topic : str
            The Kafka topic to write the messages to.
        mode : str
            The output mode for the streaming query (e.g., "append", "complete").
        checkpoint_location : str
            The location to store checkpoint information for the streaming query.

        Returns
        -------
        pyspark.sql.streaming.StreamingQuery
            A streaming query object managing the data flow to Kafka.

        Examples
        --------
        >>> df_transformed = df.withColumn("processed", lit(True))
        >>> connector = KafkaConnector("kafka:29092", spark)
        >>> query = connector.write_stream_df_to_topic(df_transformed, "topic_out", "append", "/path/to/checkpoint")
        """
        return (
            df.selectExpr("CAST(key AS STRING) AS key", "to_json(struct(*)) AS value")
                .writeStream 
                .format("kafka") 
                .outputMode(mode)
                .option("checkpointLocation", checkpoint_location)
                .option("kafka.bootstrap.servers", self._bootstrap_server) 
                .option("topic", topic) 
                .start()
            )