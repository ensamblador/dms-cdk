

from aws_cdk import (
    aws_dms as dms,
    aws_ec2 as ec2,
    core,
)

from project_config import (
    DMS_INSTANCE_CLASS,
    DMS_STORAGE,
    VPC_NAME
)


class DMSInstance(core.Construct):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = ec2.Vpc.from_lookup(
            self, "VPC",
            vpc_name=VPC_NAME
        )

        subnets = self.vpc.select_subnets(one_per_az=True)

        self.sec_group = ec2.SecurityGroup(
            self, "Acceso a DMS",
            allow_all_outbound=True,
            description="Agregar este SG al al SG de SQL Server",
            vpc=self.vpc
        )

        sn_groups= dms.CfnReplicationSubnetGroup(
            self, 
            "sngroup", 
            replication_subnet_group_description = 'Subnet Group para la migracion de SQL Server a S3', 
            replication_subnet_group_identifier = 'cdk-subnet-group',
            subnet_ids = [s.subnet_id for s in subnets.subnets])



        replication_instance =  dms.CfnReplicationInstance(
            self, "replicationInstance",
            replication_instance_class =DMS_INSTANCE_CLASS, 
            allocated_storage=DMS_STORAGE, 
            publicly_accessible=False,
            replication_subnet_group_identifier =sn_groups.replication_subnet_group_identifier,
            vpc_security_group_ids = [self.sec_group.security_group_id],
            replication_instance_identifier='SQL-2-S3')
            
        replication_instance.add_depends_on(sn_groups)
        self.instance = replication_instance

