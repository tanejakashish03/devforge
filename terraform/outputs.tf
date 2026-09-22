output "vpc_id" {
  description = "ID of the DevForge VPC"
  value       = aws_vpc.devforge.id
}

output "public_subnet_id" {
  description = "ID of the DevForge public subnet"
  value       = aws_subnet.public.id
}

output "security_group_id" {
  description = "ID of the DevForge security group"
  value       = aws_security_group.devforge.id
}

output "ec2_instance_id" {
  description = "ID of the DevForge EC2 instance"
  value       = aws_instance.devforge.id
}

output "ec2_public_ip" {
  description = "Public IP address of the DevForge EC2 instance"
  value       = aws_instance.devforge.public_ip
}

output "ec2_public_dns" {
  description = "Public DNS name of the DevForge EC2 instance"
  value       = aws_instance.devforge.public_dns
}