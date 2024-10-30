#!/bin/bash


# Ask user if they want to prune unused Docker objects before proceeding
echo "Do you want to clean up unused Docker images, volumes, and networks before building and running services? (This cannot be undone)"
echo "Enter 1 for YES, any other key for NO:"
read user_input

docker compose down

if [ "$user_input" = "1" ]; then
    echo "Running Docker system prune..."
    docker system prune -a --volumes -f
else
    echo "Skipping Docker system prune."
fi


# Build and run services defined in the first Docker Compose file
echo "Building Docker images..."
docker compose build

docker compose run django python manage.py makemigrations
docker compose run django python manage.py migrate
docker compose run django python manage.py sample_user_data
docker compose run django python manage.py load_fuel_station_data
docker compose up -d

echo "Services for docker-compose.yml have been started successfully."
