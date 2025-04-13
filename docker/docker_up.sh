echo "Building dev env container"
docker compose --file ./dev_env/docker-compose.yml --env-file .env up -d

echo "Building Airflow containers..."
docker compose --file ./airflow/docker-compose.yml --env-file .env up -d

echo "Building localstack AWS containers..."
docker compose --file ./aws/docker-compose.yml --env-file .env up -d

echo "Building dbt containers..."
docker compose --file ./dbt/docker-compose.yml --env-file .env up -d

echo "Building Spark containers..."
docker compose --file ./spark/docker-compose.yml --env-file .env up -d
