#!/bin/env python


import pprint
import sys
import boto3
import json



cf_client = boto3.client('cloudformation')

event = "create"

# [AutoScalingGroup].	AssociatePublicIpAddress field can not be specified without a subnet id

create_resource = json.dumps(
{
    "Parameters":{
        "Vpc":{
        
            "Type": "String",
            "Default":"vpc-23fc4145"
        }
    },
    "Resources":{
        "Subnet":{
            "Type":"AWS::EC2::Subnet",
            "Properties":{
                "AvailabilityZone":"us-west-2b",
                "CidrBlock":"172.31.0.0/24",
                "VpcId":{"Ref":"Vpc"}
            }
        },        
        "Ec2instance":{
            "Type":"AWS::EC2::Instance",
            "Properties": {
                "AvailabilityZone":"us-west-2b",
                "InstanceType":"t2.small",
                "ImageId":"ami-aa5ebdd2",
                "SubnetId":{"Ref":"Subnet"}
            }
        },
        "LaunchConfiguration":{
            "Type":"AWS::AutoScaling::LaunchConfiguration",
            "Properties":{
                "ImageId":"ami-aa5ebdd2",
                "InstanceId":{"Ref":"Ec2instance"},
                "InstanceType":"t2.small"
            }
        },
        "LoadBalancer":{
            "Type":"AWS::ElasticLoadBalancing::LoadBalancer",
            "Properties":{
                "Subnets":[{"Ref":"Subnet"}],
                "Instances":[{"Ref":"Ec2instance"}],
                "LoadBalancerName":"MyBotoELB",
                "Listeners":[
                        {
                            "LoadBalancerPort":"80",
                            "Protocol":"HTTP",
                            "InstancePort":"80"
                        }
                    ]
            }
        },        
        "AutoScalingGroup":{
            "Type":"AWS::AutoScaling::AutoScalingGroup",
            "Properties":{
                "AvailabilityZones":["us-west-2b"],
                "DesiredCapacity":"1",
                "MinSize":"1",
                "MaxSize":"1",
                "LaunchConfigurationName":{"Ref":"LaunchConfiguration"},
                "LoadBalancerNames":[{"Ref":"LoadBalancer"}],
            }
        }
    }
})

update_resource = json.dumps(
{
    "Parameters":{
            "Vpc": "vpc-23fc4145"
    },
    "Resources": {
        "Vpc":{
            "Type": "AWS::EC2::VPC",
            "Properties": {
                    "EnableDnsSupport":"true",
                    "EnableDnsHostnames":"true",
                    "CidrBlock":"172.31.0.0/16"
            }
        },
        "Subnet":{
            "Type":"AWS::EC2::Subnet",
            "Properties":{
                "AvailabilityZone":"us-west-2b",
                "CidrBlock":"172.31.0.0/24",
                "VpcId":{"Ref":"Vpc"}
            }
        },
        "PlacementGroup":{
            "Type":"AWS::EC2::PlacementGroup"
        },
        "NetworkInterface":{
            "Type":"AWS::EC2::NetworkInterface",
            "Properties":{
                "SubnetId":{"Ref":"Subnet"}
            }
        },
        "Ec2instance":{
            "Type":"AWS::EC2::Instance",
            "Properties": {
                "AvailabilityZone":"us-west-2b",
                "InstanceType":"t2.small",
                "ImageId":"ami-aa5ebdd2",
                "PlacementGroupName":{"Ref":"PlacementGroup"},
                "SubnetId":{"Ref":"Subnet"}
            }
        },
        "LaunchConfiguration":{
            "Type":"AWS::AutoScaling::LaunchConfiguration",
            "Properties":{
                "ImageId":"ami-aa5ebdd2",
                "InstanceId":{"Ref":"Ec2instance"},
                "InstanceType":"t2.small"
            }
        },
        "LoadBalancer":{
            "Type":"AWS::ElasticLoadBalancing::LoadBalancer",
            "Properties":{
                "Instances":[{"Ref":"Ec2instance"}],
                "LoadBalancerName":"MyBotoELB"
            }
        },
        "AutoScalingGroup":{
            "Type":"AWS::AutoScaling::AutoScalingGroup",
            "Properties":{
                "AvailabilityZones":["us-west-2b"],
                "DesiredCapacity":"1",
                "MinSize":"1",
                "MaxSize":"1",
                "LaunchConfigurationName":{"Ref":"LaunchConfiguration"},
                "LoadBalancerNames":[{"Ref":"LoadBalancer"}],
                "PlacementGroup":{"Ref":"PlacementGroup"}
            }
        },
        "RouteTable":{
            "Type":"AWS::EC2::RouteTable",
            "Properties":{
                "VpcId":{"Ref":"Vpc"}
            }
        },
        "InternetGateway":{
            "Type":"AWS::EC2::InternetGateway"
        }
    }
})
response=None
if event is "create":
    response = cf_client.create_stack(
            StackName='boto3-test-stack',
            TemplateBody=create_resource
        )
    
pprint.pprint(response)
