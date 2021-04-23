from os import pathconf
import pandas as pd
tickets_files = "s3://dmscdkstack-targetbucket82376b43-9lyw1htw5ynk/dms_sample/dbo/sporting_event/LOAD00000001.parquet"
tickets = pd.read_parquet(tickets_files)
print(tickets)

tickets_new = tickets.groupby('home_team_id').max()
print(tickets_new)

output_bucket = "s3://dmscdkstack-processedbucketcba354d5-1rkvr5tg7b3qq"
path = 'proccessed'
key = 'tickets_by_home_team'
tickets_new.to_parquet("{}/{}/{}".format(output_bucket, path, key))

print ('trabajo finalizado!')