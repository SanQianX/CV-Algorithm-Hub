# CV Algorithm Hub Project
# =======================

This is a computer vision algorithm hub project with a modular architecture.

## Project Structure

```
CV-Algorithm-Hub/
├── .github/workflows/      # CI/CD configurations
├── configs/                # Configuration files
│   ├── environments/       # Environment-specific configs
│   └── services/           # Service configurations
├── docs/                   # Project documentation
├── scripts/                # Deployment and management scripts
├── tests/                  # Test files
├── docker/                 # Docker-related files
│   └── nginx/              # Nginx configurations
├── src/                    # Source code
│   ├── api-gateway/        # Unified API entry layer
│   ├── algorithm-manager/  # Algorithm management layer
│   ├── task-orchestrator/  # Task orchestration layer
│   ├── algorithm-engine/   # Execution engine layer
│   ├── data-manager/       # Data flow management layer
│   ├── monitoring/         # Monitoring analysis layer
│   ├── shared/             # Shared components
│   └── web-ui/             # Frontend application
└── docker-compose.yml      # Docker orchestration
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- NVIDIA Docker Runtime (for GPU support)
- Git

### Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd CV-Algorithm-Hub
```

2. Start development services:
```bash
docker-compose up -d
```

3. Access the application:
- Web UI: http://localhost:3000
- API Docs: http://localhost:8080/docs
- Monitoring: http://localhost:8085

### Local Development

#### Python Backend

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn src.api_gateway.app.main:app --reload --port 8080
```

#### Frontend

```bash
cd src/web-ui
npm install
npm run dev
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Vue 3 + TypeScript + TailwindCSS |
| Backend | Python 3.10 + FastAPI + Pydantic |
| Database | PostgreSQL 14 + Redis |
| Message Queue | RabbitMQ / Redis Streams |
| Containerization | Docker + Docker Compose |
| GPU | NVIDIA CUDA 11.8 + cuDNN |

## Configuration

Environment-specific configurations are located in `configs/environments/`:

- `development.yaml` - Local development settings
- `staging.yaml` - Staging environment settings
- `production.yaml` - Production environment settings

Copy the appropriate template and modify as needed:

```bash
cp configs/environments/development.yaml configs/environments/development.local.yaml
```

## API Documentation

All API endpoints are documented using OpenAPI (Swagger). Access the documentation at:

- Development: http://localhost:8080/docs
- Staging: https://staging-api.cvhub.example.com/docs
- Production: https://api.cvhub.example.com/docs

## Testing

```bash
# Run Python tests
pytest tests/ -v --cov=src

# Run frontend tests
cd src/web-ui
npm run test
```

## CI/CD

The project uses GitHub Actions for CI/CD:

- **CI Pipeline**: Runs on every push/PR
  - Code linting (Black, isort, ruff, MyPy)
  - Frontend linting (ESLint, Prettier)
  - Unit tests with coverage
  - Docker image building

- **CD Pipeline**: Runs on main branch after CI passes
  - Deploys to staging environment
  - Requires manual approval for production

## License

MIT License
