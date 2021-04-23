import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import re

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)
## @type: DataSource
## @args: [database = "dms_sample", table_name = "sporting_event_ticket", transformation_ctx = "DataSource0"]
## @return: DataSource0
## @inputs: []
DataSource0 = glueContext.create_dynamic_frame.from_catalog(database = "dms_sample", table_name = "sporting_event_ticket", transformation_ctx = "DataSource0")
## @type: Filter
## @args: [f = lambda row : (row["ticket_price"] > 50000), transformation_ctx = "Transform0"]
## @return: Transform0
## @inputs: [frame = DataSource0]
Transform0 = Filter.apply(frame = DataSource0, f = lambda row : (row["ticket_price"] > 50000), transformation_ctx = "Transform0")
## @type: DataSink
## @args: [connection_type = "s3", format = "parquet", connection_options = {"path": "s3://dmscdkstack-processedbucketcba354d5-1rkvr5tg7b3qq/processed/", "partitionKeys": []}, transformation_ctx = "DataSink0"]
## @return: DataSink0
## @inputs: [frame = Transform0]
DataSink0 = glueContext.write_dynamic_frame.from_options(frame = Transform0, connection_type = "s3", format = "parquet", connection_options = {"path": "s3://dmscdkstack-processedbucketcba354d5-1rkvr5tg7b3qq/processed/", "partitionKeys": []}, transformation_ctx = "DataSink0")
job.commit()