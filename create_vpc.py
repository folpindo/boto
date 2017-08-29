#!/bin/env python

import pprint
import sys
import boto3
import json

cf_client = boto3.client('cloudformation')

event = "update"
orig_resource = json.dumps(
{
    "Parameters":{
        "Vpc":{
        
            "Type": "String",
            "Default":"vpc-3e2ad758"
        },
        "WebhookGroupName":{
            "Type":"String",
            "Default":"WebhookGroup"
        },
        "WebhookInstanceType":{
            "Type":"String",
            "Default":"t2.small"
        },
        "StackName":{
            "Type":"String",
            "Default":"usap-dev-stack"
        },
        "WebhookAmi":{
            "Type":"String",
            "Default":"ami-aa5ebdd2"
        }
        
    },
    "Mappings" : {
        "Region2Examples" : {
              "us-west-2" : { "Examples" : "https://s3-us-west-2.amazonaws.com/cloudformation-examples-us-west-2" }
          }
    },
    "Resources":{
        "Subnet":{
            "Type":"AWS::EC2::Subnet",
            "Properties":{
                "AvailabilityZone":"us-west-2b",
                "CidrBlock":"172.16.0.0/24",
                "VpcId":{"Ref":"Vpc"}
            }
        }
    }
})

update_resource = json.dumps(
{
    "Parameters":{
        "Vpc":{
        
            "Type": "String",
            "Default":"vpc-3e2ad758"
        },
        "WebhookGroupName":{
            "Type":"String",
            "Default":"WebhookGroup"
        },
        "WebhookInstanceType":{
            "Type":"String",
            "Default":"t2.small"
        },
        "StackName":{
            "Type":"String",
            "Default":"usap-dev-stack"
        },
        "WebhookAmi":{
            "Type":"String",
            "Default":"ami-aa5ebdd2"
        },
        "KeyName":{
            "Type":"String",
            "Default":"kube-dev-instance"
        }
    },
    "Mappings" : {
        "Region2Examples" : {
              "us-west-2" : { "Examples" : "https://s3-us-west-2.amazonaws.com/cloudformation-examples-us-west-2" }
          }
    },    
    "Resources":{
        "Subnet":{
            "Type":"AWS::EC2::Subnet",
            "Properties":{
                "AvailabilityZone":"us-west-2b",
                "CidrBlock":"172.16.0.0/24",
                "VpcId":{"Ref":"Vpc"}
            }
        },
        "WebhookGroup":{
            "Type":"AWS::AutoScaling::AutoScalingGroup",
            "Properties":{
                "AvailabilityZones":{"Fn::GetAZs":""},
                "LaunchConfigurationName" : { "Ref" : "WebhookInstanceLaunchConfiguration" },
                "MinSize" : "1",
                "MaxSize" : "1",
                "LoadBalancerNames" : [ { "Ref" : "WebhookInstanceLoadBalancer" } ],
                "CreationPolicy" : {
                    "ResourceSignal" : {
                        "Timeout" : "PT15M",
                          "Count"   : "1"
                    }
                },
                "UpdatePolicy": {
                    "AutoScalingRollingUpdate": {
                        "MinInstancesInService": "1",
                        "MaxBatchSize": "1",
                        "PauseTime" : "PT15M",
                        "WaitOnResourceSignals": "true"
                    }
                }                
            }
        },
    "WebhookInstanceLaunchConfiguration" : {
      "Type" : "AWS::AutoScaling::LaunchConfiguration",
      "Metadata" : {
        "Comment" : "Install a simple application",
        "AWS::CloudFormation::Init" : {
          "config" : {
            "packages" : {
              "yum" : {
                "httpd" : []
              }
            },

            "files" : {
              "/var/www/html/index.html" : {
                "content" : { "Fn::Join" : ["\n", [
                  "<img src=\"", {"Fn::FindInMap" : ["Region2Examples", {"Ref" : "AWS::Region"}, "Examples"]}, "/cloudformation_graphic.png\" alt=\"AWS CloudFormation Logo\"/>",
                  "<h1>Congratulations, you have successfully launched the AWS CloudFormation sample.</h1>"
                ]]},
                "mode"    : "000644",
                "owner"   : "root",
                "group"   : "root"
              },

              "/etc/cfn/cfn-hup.conf" : {
                "content" : { "Fn::Join" : ["", [
                  "[main]\n",
                  "stack=", { "Ref" : "AWS::StackId" }, "\n",
                  "region=", { "Ref" : "AWS::Region" }, "\n"
                ]]},
                "mode"    : "000400",
                "owner"   : "root",
                "group"   : "root"
              },

              "/etc/cfn/hooks.d/cfn-auto-reloader.conf" : {
                "content": { "Fn::Join" : ["", [
                  "[cfn-auto-reloader-hook]\n",
                  "triggers=post.update\n",
                  "path=Resources.LaunchConfig.Metadata.AWS::CloudFormation::Init\n",
                  "action=/opt/aws/bin/cfn-init -v ",
                  "         --stack ", { "Ref" : "AWS::StackName" },
                  "         --resource LaunchConfig ",
                  "         --region ", { "Ref" : "AWS::Region" }, "\n",
                  "runas=root\n"
                ]]}
              }
            },

            "services" : {
              "sysvinit" : {
                "httpd"    : { "enabled" : "true", "ensureRunning" : "true" },
                "cfn-hup" : { "enabled" : "true", "ensureRunning" : "true",
                              "files" : ["/etc/cfn/cfn-hup.conf", "/etc/cfn/hooks.d/cfn-auto-reloader.conf"]}
              }
            }
          }
        }
      },
      "Properties" : {
        "KeyName" : { "Ref" : "KeyName" },
        "ImageId" : "ami-aa5ebdd2",
        "SecurityGroups" : [ { "Ref" : "WebhookInstanceSecurityGroup" } ],
        "InstanceType" : "t2.small",
        "UserData"       : { "Fn::Base64" : { "Fn::Join" : ["", [
             "#!/bin/bash -xe\n",
             "yum update -y aws-cfn-bootstrap\n",

             "/opt/aws/bin/cfn-init -v ",
             "         --stack ", { "Ref" : "AWS::StackName" },
             "         --resource WebhookInstanceLaunchConfiguration ",
             "         --region ", { "Ref" : "AWS::Region" }, "\n",

             "/opt/aws/bin/cfn-signal -e $? ",
             "         --stack ", { "Ref" : "AWS::StackName" },
             "         --resource WebhookGroup",
             "         --region ", { "Ref" : "AWS::Region" }, "\n"
        ]]}}
      }
    },

    "WebServerScaleUpPolicy" : {
      "Type" : "AWS::AutoScaling::ScalingPolicy",
      "Properties" : {
        "AdjustmentType" : "ChangeInCapacity",
        "AutoScalingGroupName" : { "Ref" : "WebhookGroupName" },
        "Cooldown" : "60",
        "ScalingAdjustment" : "1"
      }
    },
    "WebServerScaleDownPolicy" : {
      "Type" : "AWS::AutoScaling::ScalingPolicy",
      "Properties" : {
        "AdjustmentType" : "ChangeInCapacity",
        "AutoScalingGroupName" : { "Ref" : "WebhookGroupName" },
        "Cooldown" : "60",
        "ScalingAdjustment" : "-1"
      }
    },

    "CPUAlarmHigh": {
     "Type": "AWS::CloudWatch::Alarm",
     "Properties": {
        "AlarmDescription": "Scale-up if CPU > 90% for 10 minutes",
        "MetricName": "CPUUtilization",
        "Namespace": "AWS/EC2",
        "Statistic": "Average",
        "Period": "300",
        "EvaluationPeriods": "2",
        "Threshold": "90",
        "AlarmActions": [ { "Ref": "WebServerScaleUpPolicy" } ],
        "Dimensions": [
          {
            "Name": "AutoScalingGroupName",
            "Value": { "Ref": "WebhookGroup" }
          }
        ],
        "ComparisonOperator": "GreaterThanThreshold"
      }
    },
    "CPUAlarmLow": {
     "Type": "AWS::CloudWatch::Alarm",
     "Properties": {
        "AlarmDescription": "Scale-down if CPU < 70% for 10 minutes",
        "MetricName": "CPUUtilization",
        "Namespace": "AWS/EC2",
        "Statistic": "Average",
        "Period": "300",
        "EvaluationPeriods": "2",
        "Threshold": "70",
        "AlarmActions": [ { "Ref": "WebServerScaleDownPolicy" } ],
        "Dimensions": [
          {
            "Name": "AutoScalingGroupName",
            "Value": { "Ref": "WebhookGroup" }
          }
        ],
        "ComparisonOperator": "LessThanThreshold"
      }
    },        
        "WebhookInstanceLoadBalancer":{
            "Type":"AWS::ElasticLoadBalancing::LoadBalancer",
            "Properties":{
                "AvailabilityZones":{"Fn::GetAZs":""},
                "Subnets":[{"Ref":"Subnet"}],
                "LoadBalancerName":"WebhookLoadBalancer",
                "Listeners":[
                        {
                            "LoadBalancerPort":"443",
                            "Protocol":"HTTPS",
                            "InstancePort":"443"
                        },
                        {
                            "LoadBalancerPort":"80",
                            "Protocol":"HTTP",
                            "InstancePort":"80"
                        }                        
                ],
                "HealthCheck":{
                    "Target":"HTTP:80/",
                    "HealthyThreshold":"3",
                    "UnhealthyThreshold":"5",
                    "Interval":"30",
                    "Timeout":"5"
                }
                
            }
        },           
        "WebhookInstanceSecurityGroup":{
            "Type":"AWS::EC2::SecurityGroup",
            "Properties":{
                "GroupName":"WebhookGroupName",
                "SecurityGroupEgress":[
                    {
                        "IpProtocol":"tcp",
                        "FromPort":"All",
                        "ToPort":"All",
                        "Cidrip":"0.0.0.0/0"
                    }                
                ],
                "SecurityGroupIngress":[
                    {
                        "IpProtocol":"tcp",
                        "FromPort":"22",
                        "ToPort":"22",
                        "Cidrip":"222.127.29.66/32"
                    },
                    {
                        "IpProtocol":"tcp",
                        "FromPort":"22",
                        "ToPort":"22",
                        "Cidrip":"64.118.163.96/27"
                    },
                    {
                        "IpProtocol":"tcp",
                        "FromPort":"443",
                        "ToPort":"443",
                        "Cidrip":"222.127.29.66/32"
                    },
                    {
                        "IpProtocol":"tcp",
                        "FromPort":"443",
                        "ToPort":"443",
                        "Cidrip":"64.118.163.96/27"
                    },
                   {
                        "IpProtocol":"tcp",
                        "FromPort":"443",
                        "ToPort":"443",
                        "SourceSecurityGroupOwnerId":{"Fn::GetAtt":["WebhookInstanceLoadBalancer","SourceSecurityGroup.OwnerAlias"]},
                        "SourceSecurityGroupName":{"Fn::GetAtt":["WebhookInstanceLoadBalancer","SourceSecurityGroup.GroupName"]}
                    },
                   {
                        "IpProtocol":"tcp",
                        "FromPort":"80",
                        "ToPort":"80",
                        "SourceSecurityGroupOwnerId":{"Fn::GetAtt":["WebhookInstanceLoadBalancer","SourceSecurityGroup.OwnerAlias"]},
                        "SourceSecurityGroupName":{"Fn::GetAtt":["WebhookInstanceLoadBalancer","SourceSecurityGroup.GroupName"]}
                    },                        
                ],
                "VpcId":{"Ref":"Vpc"}
            },
            
        }
    },
    "Outputs":{
                "URL":{
                    "Value" :  { "Fn::Join" : [ "", [ "http://", { "Fn::GetAtt" : [ "WebhookInstanceLoadBalancer", "DNSName" ]}]]}
                }
            }    
})
if event is "create":
    response = cf_client.create_stack(
            StackName='usap-dev-stack',
            TemplateBody=create_resource
        )

response=None
if event is "update":
    response = cf_client.update_stack(
            StackName='usap-dev-stack',
            TemplateBody=update_resource
        )
pprint.pprint(response)
