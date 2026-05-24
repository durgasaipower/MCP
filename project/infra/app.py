"""CDK App entry point."""

import aws_cdk as cdk
from stacks.storage_stack import StorageStack
from stacks.database_stack import DatabaseStack
from stacks.compute_stack import ComputeStack
from stacks.ingestion_stack import IngestionStack

app = cdk.App()

env = cdk.Environment(
    account=app.node.try_get_context("account"),
    region=app.node.try_get_context("region") or "us-east-1",
)

# Deploy stacks
storage = StorageStack(app, "DocsMcpStorage", env=env)
database = DatabaseStack(app, "DocsMcpDatabase", env=env)
compute = ComputeStack(app, "DocsMcpCompute", env=env, bucket=storage.bucket)
ingestion = IngestionStack(
    app, "DocsMcpIngestion", env=env,
    bucket=storage.bucket,
    database=database,
)

app.synth()
