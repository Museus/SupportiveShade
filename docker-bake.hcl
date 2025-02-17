group "default" {
  targets = ["bot"]
}

variable "BUILD_VERSION" {
  # Provide with `git describe --tags`
  default="Unknown"
}

variable "COMMIT_SHA" {
  # Provide with `git rev-parse HEAD`
  default="Unknown"
}

variable "BUILD_TIMESTAMP" {
  # Provide with `date --rfc-3339='seconds' --utc`
  default="Unknown"
}

variable "BRANCH_NAME" {
  # Provide with `git rev-parse --abbrev-ref HEAD`
  default="Unknown"
}

variable "COMMIT_TAG" {
  default = BRANCH_NAME == "main" ? "${COMMIT_SHA}" : "${BRANCH_NAME}-${COMMIT_SHA}"
}

variable "VERSION_TAG" {
      default = BRANCH_NAME == "main" ? "${BUILD_VERSION}" : "${BRANCH_NAME}-${BUILD_VERSION}"
}

variable "LATEST_TAG" {
  default = BRANCH_NAME == "main" ? "latest" : "${BRANCH_NAME}-latest"
}

target "bot" {
  context = "src"
  dockerfile = "Dockerfile"
  args = {
    BRANCH_NAME="${BRANCH_NAME}",
    BUILD_VERSION="${BUILD_VERSION}",
    BUILD_TIMESTAMP="${BUILD_TIMESTAMP}",
  }
  tags = [
    "ghcr.io/museus/supportiveshade:${COMMIT_TAG}",
    "ghcr.io/museus/supportiveshade:${VERSION_TAG}",
    "ghcr.io/museus/supportiveshade:${LATEST_TAG}",
  ]
}