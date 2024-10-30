# Summary of My Work
### Nearly Beats Google Maps with an Average Response Time of 1.5 to 3.5 Seconds

## 1. Processing the Fuel Station Data

- **Python Script `re_format_csv.py`**: Adds three extra columns (`FullAddress`, `Latitude`, `Longitude`) to the provided CSV file. The `FullAddress` column is a concatenation of `address`, `city`, and `state`, with `Latitude` and `Longitude` initially empty.
  
- **Geolocation Script `get_geo_location_from_address.py`**: Uses OpenCage Data to retrieve geolocation data for addresses. Implemented multithreading to accelerate the process, along with a pause-and-resume mechanism to manage the free tier's request limit of 2500. With over 8000 rows, the script pauses upon reaching service limits and resumes after an API key switch.

## 2. Creating the Django Project for Optimal Routes

- **Django Project Setup**: Created a Django 3.2 project with a database for permanent data storage and Redis caching for faster data retrieval.
  
- **Django Management Commands**: Commands for bulk loading fuel station data into the database (over 8000 records) in a single query, with additional functionality to load this data into Redis for faster access.

- **API Development**: Created an API endpoint `optimal-route/` using `OptimalRouteView(APIView)` in `best_route/views.py`. This endpoint uses a `RouteManagement()` object from `best_route/utils.py` to handle routes, leveraging `scipy.spatial.cKDTree` for efficient spatial queries on cached fuel station data.

## 3. Fetching and Calculating Routes

- **Map Services Integration**: Integrated the MapQuest API, using the `fetch_route_from_mapquest` function to retrieve route options based on starting and ending coordinates.
  
- **Iterating Through Routes**: Iterates through route options to find the optimal route based on specified requirements.

- **Challenges and Solutions**: Faced a significant challenge when trying to find the nearest fuel stations along the route, as iterating through 8000+ rows was not efficient. Solved this by using `cKDTree` from `scipy.spatial`, which represents a k-dimensional (KD) tree structure optimized using Cython for superior speed. This is ideal for handling extensive datasets and performing swift nearest neighbor lookups in multiple dimensions.

- **Final Output**: Returns the optimized route. **Note**: If no route is found based on requirements, the response will state "No Optimal Route Found with fuel stations within the specified radius."

## Docker Setup

> **Note:** Running the project in Docker is recommended.

1. Update the `.env.docker` file in the project directory.

```dotenv
# Debug configuration
DEBUG=True

# Database configuration
DB_HOST=dev_db
DB_NAME=best_route_db
DB_USER=postgres
DB_PASSWORD=<YOUR_DB_PASSWORD># also update in the docker compose file with the same value
DB_PORT=5446

# Secret key (Use a secure secret in production)
SECRET_KEY='<YOUR_SECRET_KEY>'

# Redis configuration
REDIS_HOST=dev_redis
REDIS_PORT=6399

# API keys
API_KEY='<YOUR_MAPQUEST_API_KEY>'  # Obtain from https://developer.mapquest.com/
```

2. Deploy the project:

   - **For Mac and Linux**:
     ```bash
     bash scripts/mac-linux/live_server_deploy.sh
     ```
   - **For Windows**:
     ```powershell
     .\scripts\windows\live_server_deploy.ps1
     ```

   - **Alternative/Manual Commands for Windows/Mac/Linux**:
     ```bash
     docker compose build
     docker compose run django python manage.py makemigrations
     docker compose run django python manage.py migrate
     docker compose run django python manage.py sample_user_data
     docker compose run django python manage.py load_fuel_station_data
     docker compose up -d
     ```

## API Documentation for `optimal-route`

### Endpoint
`POST /optimal-route/`

### Request Example (cURL)
```bash
curl --location 'http://127.0.0.1:8000/optimal-route/' \
--header 'Content-Type: application/json' \
--data '{
  "start": "39.988997, -75.155853",
  "finish": "34.022226, -81.013437"
}'
```

## Contact

- **GitHub**: [itsmahadi007](https://github.com/itsmahadi007)
- **LinkedIn**: [Mahadi Hassan](https://linkedin.com/in/itsmahadi007)
- **Personal Website**: [mahadihassan.com](https://mahadihassan.com/)
- **Resume**: [Download PDF](https://www.mahadihassan.com/Mahadi's_Resume.pdf)

### Open Source Contributions

- **Django Advance Thumbnail Package**
  - **PyPI**: [django-advance-thumbnail](https://pypi.org/project/django-advance-thumbnail/)
  - **GitHub**: [Django Advance Thumbnail Repository](https://github.com/itsmahadi007/django_advance_thumbnail)

---

### Additional Notes

- **Security**: Replace placeholders in `.env.docker` (`<YOUR_DB_PASSWORD>`, `<YOUR_SECRET_KEY>`, `<YOUR_MAPQUEST_API_KEY>`) with secure values.
- **Optimization**: Adjust Redis and Django configurations as needed to optimize for production.
