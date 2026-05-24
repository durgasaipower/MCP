"""S3 bucket for documentation storage."""

import aws_cdk as cdk
from aws_cdk import aws_s3 as s3
from constructs import Construct


class StorageStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.bucket = s3.Bucket(
            self, "DocsBucket",
            bucket_name=f"docs-mcp-content-{cdk.Aws.ACCOUNT_ID}",
            removal_policy=cdk.RemovalPolicy.RETAIN,
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        cdk.CfnOutput(self, "BucketName", value=self.bucket.bucket_name)
