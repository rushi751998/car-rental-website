# Docker Setup Guide

This guide explains how to run the Car Rental Website application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed (usually comes with Docker Desktop)

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Clone the repository** (if not already done)
   ```bash
   git clone <repository-url>
   cd car-rental-website
   ```

2. **Set up environment variables** (optional)
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

3. **Build and run the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`

5. **Stop the application**
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker directly

1. **Build the Docker image**
   ```bash
   docker build -t car-rental-website .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     -p 5000:5000 \
     -v $(pwd)/rental.db:/app/rental.db \
     -v $(pwd)/images:/app/images \
     -e OPENAI_API_KEY=your_api_key \
     -e WHATSAPP_PHONE=+919876543210 \
     --name car-rental-app \
     car-rental-website
   ```

3. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`

4. **Stop the container**
   ```bash
   docker stop car-rental-app
   docker rm car-rental-app
   ```

## Environment Variables

The application supports the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host address | `0.0.0.0` |
| `PORT` | Server port | `5000` |
| `OPENAI_API_KEY` | OpenAI API key for chat functionality | (empty) |
| `WHATSAPP_PHONE` | WhatsApp contact number | `+919876543210` |

## Data Persistence

The Docker setup includes volume mounts for:
- **Database**: `./rental.db` - SQLite database for storing application data
- **Images**: `./images` - User-uploaded car images and other media

This ensures your data persists even when containers are stopped or removed.

## Useful Docker Commands

### View running containers
```bash
docker ps
```

### View container logs
```bash
docker-compose logs -f
# or
docker logs -f car-rental-app
```

### Rebuild the image
```bash
docker-compose build --no-cache
```

### Run in detached mode
```bash
docker-compose up -d
```

### Access container shell
```bash
docker exec -it car-rental-website /bin/bash
```

### Remove all containers and images
```bash
docker-compose down --rmi all --volumes
```

## Health Check

The container includes a health check that monitors the application's status:
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3

Check health status:
```bash
docker inspect --format='{{.State.Health.Status}}' car-rental-website
```

## Troubleshooting

### Port already in use
If port 5000 is already in use, modify the port mapping in `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Use port 8080 instead
```

### Permission issues with volumes
On Linux/Mac, ensure the database and images directories have correct permissions:
```bash
chmod 755 images
chmod 644 rental.db
```

### Container not starting
Check the logs for errors:
```bash
docker-compose logs
```

## Production Deployment

For production deployment, consider:
1. Using environment-specific `.env` files
2. Setting up proper HTTPS/SSL certificates
3. Configuring a reverse proxy (nginx/traefik)
4. Implementing proper backup strategies for the database
5. Using Docker secrets for sensitive data
6. Setting resource limits in docker-compose.yml

## Multi-stage Build (Advanced)

For a smaller production image, you can modify the Dockerfile to use multi-stage builds. The current Dockerfile is optimized for simplicity and ease of development.

## Support

For issues or questions, please refer to the main README.md or open an issue in the repository.
