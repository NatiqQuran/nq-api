#!/usr/bin/env bash
set -euo pipefail

sudo apt update

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

install_docker_via_script() {
  echo "🛠️ Installing Docker..."
  curl -fsSL https://get.docker.com | sh
  echo "✅ Docker installed."
}

setup_project_folder() {
  local folder="nq-api"
  echo "📁 Creating folder: $folder"
  mkdir -p "$folder"

  echo "⬇️ Downloading docker-compose.yaml"
  if ! curl -fsSL https://raw.githubusercontent.com/NatiqQuran/nq-api/refs/heads/main/docker-compose.yaml \
        -o "$folder/docker-compose.yaml"; then
        echo "❌ Failed to download docker-compose.yaml"
        exit 1
    fi

  echo "⬇️ Downloading nginx.conf"
  if ! curl -fsSL https://raw.githubusercontent.com/NatiqQuran/nq-api/refs/heads/main/nginx.conf \
        -o "$folder/nginx.conf"; then
        echo "❌ Failed to download nginx.conf"
        exit 1
    fi

  echo "✅docker-compose.yaml and nginx.conf saved to $folder."
}

customize_compose() {
  local file="$1/docker-compose.yaml"

  sed -i "/^  api:/,/^[^ ]/ s|^[[:space:]]*build:.*|    image: natiqquran/nq-api|" "$file"
  echo "🔄 Step 1: image for api set to natiqquran/nq-api"

  local secret=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 40 | head -n 1)
  sed -i "s/^ *SECRET_KEY:.*/      SECRET_KEY: $secret/" "$file"
  echo "🔒 Step 2: SECRET_KEY has been set"

  local ip=$(curl -s https://api.ipify.org)
  sed -i "s|^ *DJANGO_ALLOWED_HOSTS:.*|      DJANGO_ALLOWED_HOSTS: $ip|" "$file"
  echo "🌐 Step 3: DJANGO_ALLOWED_HOSTS set to $ip"

  echo -n "Do you want to open docker-compose.yaml for manual edit? (yes/no): "
  read -t 10 -n 1 ans || ans="n"
  echo
  ans=${ans:-n}

  case "${ans,,}" in
    yes|y)
      ${EDITOR:-vi} "$file"
      echo "✏️ Manual edit done, continuing..."
      ;;
    *)
      echo "⏩ Skipping manual edit"
      ;;
  esac
}

if [[ "${1:-}" == "no-install" ]]; then
  echo "🚫 Skipping Docker installation (no-install flag used)"
else
  if command_exists docker; then
    echo -n "⚠️ Docker is already installed. Do you want to reinstall it? (yes/no): "
    read -t 10 -n 1 reinstall || reinstall="n"
    echo
    reinstall=${reinstall:-n}
    if [[ "${reinstall,,}" =~ ^(y|yes)$ ]]; then
      install_docker_via_script
    else
      echo "⏩ Skipping Docker installation."
    fi
  else
    install_docker_via_script
  fi
fi

setup_project_folder

customize_compose "nq-api"

echo "🚀 Running docker compose up -d"
cd nq-api
docker compose up -d

echo "🎉 Mission completed!"
