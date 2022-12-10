import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def get_spark(cores=8, memory="6g", partitions=64):
    """Get a spark session for a single driver."""
    return (
        SparkSession.builder.config("spark.driver.memory", memory)
        .config("spark.driver.cores", cores)
        .config("spark.sql.shuffle.partitions", partitions)
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .getOrCreate()
    )
