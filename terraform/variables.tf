variable "region" {
  default = "us-east-1"
}

variable "vpc_cidr" {
  default = "10.0.0.0/16"
}

variable "subnet_cidr" {
  default = "10.0.1.0/24"
}

variable "ami_id" {
  default = "ami-0e001c9271cf7f3b9"
}

variable "instance_type" {
  default = "t2.micro"
}

variable "key_name" {
  default = "ilay-private-key"
}
