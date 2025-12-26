# Car Rental Website

A comprehensive car rental and picnic destination website built with FastAPI backend and modern HTML/CSS/JavaScript frontend.

## Features

- 🚗 Car rental management system
- 🏞️ Picnic destination browsing
- 💬 AI-powered chatbot using OpenAI
- 👤 User authentication and session management
- 📊 Admin dashboard
- 🗺️ Trip planning functionality

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **AI**: OpenAI GPT integration
- **Authentication**: JWT-based sessions

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Poetry (Python package manager)
- OpenAI API key (optional, for chatbot functionality)

### Installation

#### For WSL (Windows Subsystem for Linux)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd car-rental-website
   ```

2. **Run the setup script**
   ```bash
   chmod +x setup-wsl.sh
   ./setup-wsl.sh
   ```
   This script will:
   - Install Poetry if not present
   - Install all project dependencies
   - Create necessary folders
   - Set up the `.env` file

3. **Update environment variables**
   Edit the `.env` file with your configuration:
   ```env
   HOST=0.0.0.0
   PORT=5000
   OPENAI_API_KEY=your_actual_openai_api_key
   ```

4. **Start the development server**
   ```bash
   make dev
   ```

#### For Windows/macOS/Linux (Manual Setup)

1. **Install Poetry**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Create and configure .env file**
   ```bash
   cp .env.example .env  # If example exists, or create manually
   ```
   Edit `.env` with your values:
   ```env
   HOST=0.0.0.0
   PORT=5000
   OPENAI_API_KEY=your_actual_openai_api_key
   ```

4. **Run the application**
   ```bash
   poetry run uvicorn main:app --host 0.0.0.0 --port 5000 --reload
   ```

## Available Commands

Using Makefile (recommended for WSL/Linux/macOS):

```bash
make setup    # Initial setup
make dev      # Start development server with auto-reload
make prod     # Start production server
make test     # Run tests
make format   # Format code with black
make lint     # Lint code with flake8
make clean    # Clean cache and temporary files
```

Using Poetry directly:

```bash
poetry install                                              # Install dependencies
poetry run uvicorn main:app --host 0.0.0.0 --port 5000 --reload  # Dev server
poetry run uvicorn main:app --host 0.0.0.0 --port 5000          # Prod server
poetry run pytest                                            # Run tests
poetry run black .                                           # Format code
```

## Project Structure

```
car-rental-website/
├── main.py                 # FastAPI application entry point
├── .env                    # Environment variables (not in git)
├── pyproject.toml         # Poetry configuration
├── Makefile               # Make commands for easy development
├── setup-wsl.sh          # WSL setup script
├── requirements.txt       # Pip requirements (legacy)
├── rental.db             # SQLite database
├── images/               # Image assets
│   └── cars/            # Car images
├── public/              # Frontend HTML files
│   ├── index.html
│   ├── cars.html
│   ├── spots.html
│   ├── admin.html
│   └── ...
└── src/                 # Backend source code
    ├── __init__.py
    ├── utils.py         # Utilities and config
    ├── db.py           # Database models
    ├── db_ops.py       # Database operations
    ├── schemas.py      # Pydantic schemas
    └── api/            # API routes
        ├── cars.py
        ├── spots.py
        ├── users.py
        ├── chat.py
        ├── last_trips.py
        └── admin.py
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host address | `0.0.0.0` |
| `PORT` | Server port | `5000` |
| `OPENAI_API_KEY` | OpenAI API key for chatbot | _(empty)_ |

## API Endpoints

### Public Endpoints
- `GET /` - Home page
- `GET /cars.html` - Car listing page
- `GET /spots.html` - Destinations page
- `POST /api/users/register` - User registration
- `POST /api/users/login` - User login

### Protected Endpoints (require authentication)
- `GET /api/cars` - List all cars
- `GET /api/spots` - List all destinations
- `POST /api/chat` - Chat with AI assistant
- `GET /api/chat/history` - Get chat history
- `POST /api/chat/plan` - Submit trip plan

### Admin Endpoints
- `POST /api/admin/login` - Admin login
- `GET /api/admin/stats` - Get system statistics
- `POST /api/admin/cars` - Add new car
- `PUT /api/admin/cars/{id}` - Update car
- `DELETE /api/admin/cars/{id}` - Delete car

## Development

### Running in Development Mode

The development server includes auto-reload functionality:

```bash
make dev
# OR
poetry run uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

Access the application at `http://localhost:5000`

### Code Quality

Format code:
```bash
make format
# OR
poetry run black .
```

Lint code:
```bash
make lint
# OR
poetry run flake8 src/
```

## Troubleshooting

### Poetry not found after installation
Add Poetry to your PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Port already in use
Change the PORT in `.env` file or kill the process using port 5000:
```bash
# Linux/WSL
sudo lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### OpenAI API errors
- Ensure `OPENAI_API_KEY` is set correctly in `.env`
- Check your OpenAI account has credits
- The chatbot will fall back to basic responses if OpenAI is not configured

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub or contact the maintainers.
