#!/bin/bash
set -euo pipefail

AWS_REGION=ap-south-1
IMAGE=125992594191.dkr.ecr.ap-south-1.amazonaws.com/quickcart:public-demo-v2

dnf install -y docker
systemctl enable --now docker
install -d -m 0750 /var/lib/quickcart /etc/quickcart

for attempt in {1..12}; do
    if aws ecr get-login-password --region "$AWS_REGION" \
        | docker login --username AWS --password-stdin \
            125992594191.dkr.ecr.ap-south-1.amazonaws.com; then
        break
    fi
    if [ "$attempt" -eq 12 ]; then
        exit 1
    fi
    sleep 5
done

docker pull "$IMAGE"
docker logout 125992594191.dkr.ecr.ap-south-1.amazonaws.com

TOKEN=$(curl -fsS -X PUT \
    -H 'X-aws-ec2-metadata-token-ttl-seconds: 21600' \
    http://169.254.169.254/latest/api/token)
PUBLIC_IP=$(curl -fsS \
    -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/public-ipv4)
SECRET_KEY=$(openssl rand -base64 48 | tr -d '\n')

cat > /etc/quickcart/quickcart.env <<EOF
DJANGO_SECRET_KEY=$SECRET_KEY
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=$PUBLIC_IP
DJANGO_CSRF_TRUSTED_ORIGINS=http://$PUBLIC_IP
DJANGO_SQLITE_PATH=/data/db.sqlite3
DJANGO_MEDIA_ROOT=/data/media
DJANGO_SECURE_SSL_REDIRECT=false
DJANGO_SESSION_COOKIE_SECURE=false
DJANGO_CSRF_COOKIE_SECURE=false
EOF
chmod 0600 /etc/quickcart/quickcart.env

docker run --detach \
    --name quickcart \
    --restart unless-stopped \
    --publish 80:8000 \
    --env-file /etc/quickcart/quickcart.env \
    --volume /var/lib/quickcart:/data \
    "$IMAGE"

docker exec quickcart python manage.py migrate --noinput
docker exec quickcart python manage.py seed_data
