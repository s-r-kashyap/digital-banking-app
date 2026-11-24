variable "aws_region" {
  type        = string
  description = "AWS region to deploy resources"
}

variable "project_name" {
  type        = string
  description = "Project prefix used for resource naming"
}

variable "environment" {
  type        = string
  description = "Deployment environment (e.g., dev, staging, prod)"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
}

variable "az_count" {
  type        = number
  description = "Number of Availability Zones to span"
  default     = 2
}

variable "single_nat_gateway" {
  type        = bool
  description = "Use a single NAT Gateway to save costs in non-prod"
  default     = true
}

variable "eks_version" {
  type        = string
  description = "Kubernetes version for EKS"
  default     = "1.31"
}

variable "node_instance_types" {
  type        = list(string)
  description = "EC2 instance types for EKS worker nodes"
  default     = ["t3.medium"]
}

variable "node_scaling" {
  type = object({
    desired = number
    min     = number
    max     = number
  })
  default = {
    desired = 2
    min     = 1
    max     = 4
  }
}

variable "microservices" {
  type        = list(string)
  description = "List of microservice names to create ECR repositories for"
}

variable "github_repo" {
  type        = string
  description = "GitHub repository in 'owner/repo' format allowed to assume the deployment IAM role"
}

variable "app_secrets" {
  type        = map(string)
  description = "Key-value pairs stored in AWS Secrets Manager for the application"
  sensitive   = true
  default     = {}
}