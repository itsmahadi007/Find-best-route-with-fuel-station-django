# Ask user if they want to prune unused Docker objects before proceeding
Write-Host "Do you want to clean up unused Docker images, volumes, and networks before building and running services? (This cannot be undone)"
$user_input = Read-Host "Enter 1 for YES, any other key for NO"

docker compose down

if ($user_input -eq "1") {
    Write-Host "Running Docker system prune..."
    docker system prune -a --volumes -f
} else {
    Write-Host "Skipping Docker system prune."
}

# Build and run services defined in the first Docker Compose file
Write-Host "Building Docker images..."
docker compose build

Write-Host "Running migrations..."
docker compose run django python manage.py makemigrations
docker compose run django python manage.py migrate
docker compose run django python manage.py sample_user_data
docker compose run django python manage.py load_fuel_station_data
docker compose up -d

Write-Host "Services for docker-compose.yml have been started successfully."
