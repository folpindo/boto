#!/bin/env python


import pprint
import sys
import boto3
import json



cf_client = boto3.client('cloudformation')

resource_vpc = json.dumps(
{
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

response = cf_client.create_stack(
        StackName='boto3-test-stack',
        TemplateBody=resource_vpc
    )


pprint.pprint(response)
