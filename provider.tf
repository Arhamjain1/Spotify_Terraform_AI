terraform {
  required_providers {
    spotify = {
      source  = "conradludgate/spotify"
      version = "0.2.7"
    }
  }
}

provider "spotify" {
  api_key = var.api_key
}

variable "api_key" {
  description = "Spotify API Key"
  type        = string
  sensitive   = true
}

# Auto-generated playlists

