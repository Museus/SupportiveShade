group "default" {
  targets = ["bot"]
}

variable "BUILD_VERSION" {
  # Provide with `git describe --tags`
  default="Unknown"
}

variable "BUILD_TIMESTAMP" {
  # Provide with `date --rfc-3339='seconds' --utc`
  default="Unknown"
}

target "bot" {
  context = "."
  dockerfile = "Dockerfile"
  args = {
    BUILD_VERSION="${BUILD_VERSION}",
    BUILD_TIMESTAMP="${BUILD_TIMESTAMP}",
  }
  tags = [
    "ghcr.io/museus/supportiveshade:${BUILD_VERSION}",
    "ghcr.io/museus/supportiveshade:latest",
  ]
}