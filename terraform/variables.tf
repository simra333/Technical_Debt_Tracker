variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
  sensitive   = true  # Marks this as sensitive so it won't show in logs
}