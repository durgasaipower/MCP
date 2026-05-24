"""PostgreSQL with pgvector for vector storage."""

import aws_cdk as cdk
from aws_cdk import aws_rds as rds, aws_ec2 as ec2
from constructs import Construct


class DatabaseStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # VPC
        self.vpc = ec2.Vpc(
            self, "Vpc",
            max_azs=2,
            nat_gateways=1,
        )

        # Security group for DB
        self.db_sg = ec2.SecurityGroup(
            self, "DbSg",
            vpc=self.vpc,
            description="Security group for docs MCP database",
        )
        self.db_sg.add_ingress_rule(
            ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            ec2.Port.tcp(5432),
            "Allow PostgreSQL from VPC",
        )

        # RDS PostgreSQL with pgvector
        self.db_instance = rds.DatabaseInstance(
            self, "DocsDb",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_16_4,
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T4G, ec2.InstanceSize.MEDIUM,
            ),
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[self.db_sg],
            database_name="docs_mcp",
            credentials=rds.Credentials.from_generated_secret("postgres"),
            removal_policy=cdk.RemovalPolicy.SNAPSHOT,
        )

        cdk.CfnOutput(self, "DbEndpoint", value=self.db_instance.db_instance_endpoint_address)
        cdk.CfnOutput(self, "DbSecretArn", value=self.db_instance.secret.secret_arn)
