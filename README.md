# ebs_snapshot_godfather
A tool to manage EBS snapshot lifecycles following the Grandfather-father-son backup scheme. Built to run on Lambda and triggered by a CloudWatch Rule (cron).

## Why?

I wanted a simple script to manage snapshots that could run in a Lambda. AWS does offer a "Lifecycle Manager" tool but this does not support the Grandfather-father-son backup scheme.

## Required IAM Permissions
This is a basic policy for running the Lambda. You can limit its access even more to a specific volume if you would like.

The `AWSLambdaBasicExecutionRole` policy is also required.

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ec2:DeleteSnapshot",
                "ec2:CreateTags",
                "ec2:CreateSnapshot"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeSnapshotAttribute",
                "ec2:DescribeSnapshots"
            ],
            "Resource": "*"
        }
    ]
}
```

## CloudWatch Rule

You can use a CloudWatch rule to trigger the Lambda to run once a day. You will want to choose the Lambda as the target for the rule. 

Select "Constant (JSON text)" and use the following JSON:

```
{
	"managed_tag": "managed_backup",
	"volume_id": "vol-xxxxxx",
	"days_to_keep": 7,
	"weeks_to_keep": 5,
	"months_to_keep": 13
}
```

Make sure to change the `volume_id` to the volume you want to manage snapshots for and change the retentions if you would like.

## Existing and Manual Snapshots

If you make any manual snapshots or have any existing snapshots this tool will not touch them unless they have the `managed_tag` tag you defined and has the value set to `true`.