output "vpc_id" {
  value = module.vpc.vpc_id
}

output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "ecr_repository_urls" {
  value = { for k, v in aws_ecr_repository.services : k => v.repository_url }
}

output "secrets_manager_arn" {
  value = aws_secretsmanager_secret.app.arn
}

output "github_actions_role_arn" {
  value       = aws_iam_role.github_actions.arn
  description = "Set this ARN in your GitHub Actions workflow role-to-assume"
}

output "configure_kubectl" {
  value = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}