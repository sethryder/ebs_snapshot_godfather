import boto3
import datetime
from dateutil.relativedelta import relativedelta
import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_dates_to_keep(days_to_keep, weeks_to_keep, months_to_keep):
    day_base = datetime.date.today()
    week_base = day_base - datetime.timedelta(days=(day_base.weekday() - 6) % 7)

    days_list = [day_base - relativedelta(days=x) for x in range(0, days_to_keep)]
    weeks_list = [week_base - relativedelta(weeks=x) for x in range(0, weeks_to_keep)]
    month_list = [day_base - relativedelta(months=+x, day=1) for x in range(0, months_to_keep)]

    return list(dict.fromkeys(days_list + weeks_list + month_list))

def list_snapshots(volume_id, management_tag):
    client = boto3.client('ec2')

    response = client.describe_snapshots(
        Filters=[
            {
                'Name': 'tag:' + management_tag,
                'Values': [
                    "true",
                ]
            },
            {
                'Name': 'volume-id',
                'Values': [
                    volume_id,
                ]
            },
        ],
    )

    return response['Snapshots']


def create_snapshot(volume_id, management_tag):
    client = boto3.client('ec2')
    response = client.create_snapshot(
        Description='Snapshot of ' + volume_id,
        VolumeId=volume_id,
        TagSpecifications=[
            {
                'ResourceType': 'snapshot',
                'Tags': [
                    {
                        'Key': management_tag,
                        'Value': 'true'
                    },
                ]
            },
        ],
    )
    
    return response

def delete_snapshot(snapshot_id):
    client = boto3.client('ec2')
    response = client.delete_snapshot(SnapshotId=snapshot_id)

    return response

def snapshot_handler(event, context):
    volume_id = event['volume_id']
    managed_tag = event['managed_tag']
    days_to_keep = event['days_to_keep']
    weeks_to_keep = event['weeks_to_keep']
    months_to_keep = event['months_to_keep']

    logger.info("Creating new snapshot")
    create_snapshot(volume_id, managed_tag)    

    logger.info("Calculating dates we want to keep")
    dates_to_keep = get_dates_to_keep(days_to_keep, weeks_to_keep, months_to_keep)
    logger.info(dates_to_keep)

    logger.info("Getting list of current snapshots")
    current_snapshots = list_snapshots(volume_id, managed_tag)
    
    logger.info("Pruning snapshots")
    for snapshot in current_snapshots:
        if snapshot['StartTime'].date() not in dates_to_keep:
            logger.info("Deleting snapshot: " + snapshot['SnapshotId'] + " with date " + str(snapshot['StartTime'].date()))
            delete_snapshot(snapshot['SnapshotId'])