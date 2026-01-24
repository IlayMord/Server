# VPC
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr

  tags = {
    Name = "s3-file-manager-vpc"
  }
}

# Subnet (Public)
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.subnet_cidr
  map_public_ip_on_launch = true

  tags = {
    Name = "s3-file-manager-public-subnet"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "s3-file-manager-igw"
  }
}

# Route Table
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "s3-file-manager-public-rt"
  }
}

resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public_rt.id
}

# Security Group
resource "aws_security_group" "web_sg" {
  name   = "s3-file-manager-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance
resource "aws_instance" "s3_file_manager" {
  ami           = var.ami_id
  instance_type = var.instance_type

  key_name = var.key_name

  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.web_sg.id]

  user_data = <<-EOF
    #!/bin/bash
    set -e

    apt update -y
    apt install -y docker.io docker-compose git

    systemctl start docker
    systemctl enable docker

    cd /home/ubuntu

    if [ ! -d "s3-file-manager-server" ]; then
        git clone https://github.com/IlayMord/s3-file-manager-server.git
    fi

    cd s3-file-manager-server/docker
    docker-compose up -d
  EOF

  tags = {
    Name = "s3-file-manager-Server"
  }
}
