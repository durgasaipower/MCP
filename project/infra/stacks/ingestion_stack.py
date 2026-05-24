"""Lambda function triggered by S3 for document ingestion."""

import aws_cdk as cdk
from aws_cdk import (
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
)
from constructs import Construct


class IngestionStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, bucket: s3.Bucket, database, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Lambda function for ingestion
        self.ingestion_fn = _lambda.DockerImageFunction(
            self, "IngestionFn",
            code=_lambda.DockerImageCode.from_image_asset("../ingestion"),
            memory_size=1024,
            timeout=cdk.Duration.minutes(5),
            environment={
                "S3_DOCS_PREFIX": "documents/",
                "VECTOR_DB_HOST": database.db_instance.db_instance_endpoint_address,
                "VECTOR_DB_PORT": "5432",
                "VECTOR_DB_NAME": "docs_mcp",
                "EMBEDDING_MODEL": "text-embedding-3-small",
                # OPENAI_API_KEY and DB credentials via Secrets Manager
            },
            vpc=database.vpc,
            vpc_subnets=cdk.aws_ec2.SubnetSelection(
                subnet_type=cdk.aws_ec2.SubnetType.PRIVATE_WITH_EGRESS,
            ),
        )

        # Grant S3 read access
        bucket.grant_read(self.ingestion_fn)

        # S3 trigger: invoke Lambda on PutObject
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED_PUT,
            s3n.LambdaDestination(self.ingestion_fn),
            s3.NotificationKeyFilter(prefix="documents/"),
        )

        cdk.CfnOutput(self, "IngestionFnArn", value=self.ingestion_fn.function_arn)
