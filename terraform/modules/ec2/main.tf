resource "aws_instance" "s3_file_manager" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = var.key_name

  subnet_id              = var.subnet_id
  vpc_security_group_ids = [var.security_group_id]

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
