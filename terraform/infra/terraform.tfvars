aws_region         = "ap-south-1"
project_name       = "digital-banking"
environment        = "dev"
vpc_cidr           = "10.0.0.0/16"
az_count           = 2
single_nat_gateway = true
eks_version        = "1.31"

node_instance_types = ["t3.medium"]
node_scaling = {
  desired = 2
  min     = 1
  max     = 4
}

microservices = [
  "frontend-service",
  "auth-service",
  "account-service",
  "beneficiary-service",
  "payment-service",
  "transaction-service"
]

github_repo = "your-github-username/digital-banking"

app_secrets = {
  JWT_SECRET_KEY = "change-me-before-apply"
  DB_PASSWORD    = "change-me-before-apply"
}