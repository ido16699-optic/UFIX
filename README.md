# UFIX - Uber for Handymen

A platform connecting customers who need home fixes with skilled handymen.

## Features

- **Customer Features**
  - Create job requests (ASAP or scheduled)
  - Receive and compare offers from handymen
  - Real-time chat with handymen
  - Rate and review completed jobs

- **Handyman Features**
  - Browse available jobs by category and location
  - Submit offers with pricing and estimated time
  - Manage active orders
  - Build reputation through reviews

- **Admin Features**
  - Verify handyman identity documents
  - Manage users and platform settings

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database with async support (asyncpg)
- **SQLAlchemy 2.0** - Async ORM
- **JWT** - Authentication
- **WebSockets** - Real-time chat

### Frontend
- **React 18** with TypeScript
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **React Query** - Server state management
- **Zustand** - Client state management
- **React Router** - Routing

## Service Categories

1. Plumbing
2. Electrical
3. Painting
4. Furniture Assembly
5. General Handyman

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Quick Start with Docker

1. Clone the repository:
\`\`\`bash
git clone https://github.com/ido16699-optic/UFIX.git
cd UFIX
\`\`\`

2. Copy environment files:
\`\`\`bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
\`\`\`

3. Start the application:
\`\`\`bash
docker-compose up -d
\`\`\`

4. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Local Development

#### Backend

1. Create virtual environment:
\`\`\`bash
cd backend
python -m venv venv
source venv/bin/activate
\`\`\`

2. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. Set up environment:
\`\`\`bash
cp .env.example .env
\`\`\`

4. Run the server:
\`\`\`bash
uvicorn app.main:app --reload
\`\`\`

#### Frontend

1. Install dependencies:
\`\`\`bash
cd frontend
npm install
\`\`\`

2. Set up environment:
\`\`\`bash
cp .env.example .env
\`\`\`

3. Start development server:
\`\`\`bash
npm run dev
\`\`\`

## API Documentation

Once the backend is running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Business Logic

### Platform Commission
- 4.5% commission on each completed job
- Deducted from handyman payment

### Job Flow
1. Customer creates job request
2. Nearby handymen receive notifications
3. Handymen submit offers (price + estimated time)
4. Customer selects an offer
5. Job becomes an active order
6. Upon completion, customer confirms and pays
7. Both parties can leave reviews

## License

MIT
