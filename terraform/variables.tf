variable "aws_region" {
  description = "AWS region where DevForge infrastructure will be deployed"
  type        = string
  default     = "ap-south-1"
}

variable "vpc_cidr" {
  description = "CIDR block for the DevForge VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the DevForge public subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "ssh_allowed_cidr" {
  description = "CIDR block allowed to access the DevForge EC2 instance over SSH"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type for the DevForge server"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "AWS key pair name used to access the DevForge EC2 instance"
  type        = string
}