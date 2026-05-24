"""ECS Fargate service for the MCP server."""

import aws_cdk as cdk
from aws_cdk import (
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ec2 as ec2,
    aws_s3 as s3,
)
from constructs import Construct


class ComputeStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, bucket: s3.Bucket, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Import VPC from database stack (or create shared)
        # For now, create a simple one - in production, share VPC
        vpc = ec2.Vpc.from_lookup(self, "Vpc", is_default=False)

        # ECS Cluster
        cluster = ecs.Cluster(self, "Cluster", vpc=vpc)

        # Fargate service with ALB
        self.service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "McpService",
            cluster=cluster,
            cpu=512,
            memory_limit_mib=1024,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset("../mcp"),
                container_port=8000,
                environment={
                    "S3_BUCKET": bucket.bucket_name,
                    "PORT": "8000",
                },
            ),
            public_load_balancer=True,
        )

        # Grant S3 read access
        bucket.grant_read(self.service.task_definition.task_role)

        # Health check
        self.service.target_group.configure_health_check(path="/health")

        cdk.CfnOutput(self, "ServiceUrl", value=self.service.load_balancer.load_balancer_dns_name)
