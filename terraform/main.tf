resource "aws_vpc" "devforge" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name      = "devforge-vpc"
    Project   = "DevForge"
    ManagedBy = "Terraform"
  }
}

resource "aws_internet_gateway" "devforge" {
  vpc_id = aws_vpc.devforge.id

  tags = {
    Name      = "devforge-igw"
    Project   = "DevForge"
    ManagedBy = "Terraform"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.devforge.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name      = "devforge-public-subnet"
    Project   = "DevForge"
    ManagedBy = "Terraform"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.devforge.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.devforge.id
  }

  tags = {
    Name      = "devforge-public-rt"
    Project   = "DevForge"
    ManagedBy = "Terraform"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "devforge" {
  name        = "devforge-sg"
  description = "Security group for DevForge EC2 instance"
  vpc_id      = aws_vpc.devforge.id

  ingress {
    description = "Allow HTTP traffic"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow HTTPS traffic"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow SSH from trusted IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_allowed_cidr]
  }

  egress {
    description = "Allow outbound IPv4 traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name      = "devforge-sg"
    Project   = "DevForge"
    ManagedBy = "Terraform"
  }
}

resource "aws_key_pair" "devforge" {
  key_name   = var.key_name
  public_key = file("~/.ssh/id_ed25519.pub")

  tags = {
    Name      = "devforge-key"
    Project   = "DevForge"
    ManagedBy = "Terraform"
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
}

resource "aws_instance" "devforge" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  key_name      = aws_key_pair.devforge.key_name

  iam_instance_profile = aws_iam_instance_profile.devforge_ec2.name

  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.devforge.id]
  associate_public_ip_address = true

  root_block_device {
    volume_type = "gp3"
    volume_size = 20
  }

  tags = {
    Name      = "devforge-server"
    Project   = "DevForge"
    ManagedBy = "Terraform"
  }
}

resource "aws_iam_role" "devforge_ec2" {
  name = "devforge-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "ec2.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name      = "devforge-ec2-role"
    Project   = "DevForge"
    ManagedBy = "Terraform"
  }
}

resource "aws_iam_instance_profile" "devforge_ec2" {
  name = "devforge-ec2-profile"
  role = aws_iam_role.devforge_ec2.name

  tags = {
    Name      = "devforge-ec2-profile"
    Project   = "DevForge"
    ManagedBy = "Terraform"
  }
}