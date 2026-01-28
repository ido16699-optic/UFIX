# UFIX Setup Guide

## Quick Start with Docker (Recommended)

The easiest way to get UFIX up and running is using Docker Compose.

### Option 1: Using Docker Compose

1. Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:latest
    container_name: ufix-mongodb
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_DATABASE: ufix
    volumes:
      - mongodb_data:/data/db

  app:
    build: .
    container_name: ufix-app
    ports:
      - "3000:3000"
    environment:
      - MONGODB_URI=mongodb://mongodb:27017/ufix
      - JWT_SECRET=your-secret-key-change-this
      - PORT=3000
    depends_on:
      - mongodb
    volumes:
      - .:/app
      - /app/node_modules

volumes:
  mongodb_data:
```

2. Create a `Dockerfile`:

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

3. Run the application:

```bash
docker-compose up
```

4. Access the application at `http://localhost:3000`

### Option 2: Manual Setup

#### Prerequisites

- Node.js v14 or higher
- MongoDB v4.4 or higher
- npm or yarn

#### Step 1: Install MongoDB

**On Ubuntu/Debian:**
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

**On macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community@6.0
brew services start mongodb-community@6.0
```

**On Windows:**
- Download MongoDB from https://www.mongodb.com/try/download/community
- Run the installer
- Start MongoDB as a service

#### Step 2: Verify MongoDB is Running

```bash
mongosh
# You should see the MongoDB shell
# Type 'exit' to quit
```

#### Step 3: Clone and Setup UFIX

```bash
git clone https://github.com/ido16699-optic/UFIX.git
cd UFIX
npm install
```

#### Step 4: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and update:
```
MONGODB_URI=mongodb://localhost:27017/ufix
JWT_SECRET=your-random-secret-key-change-this-in-production
PORT=3000
```

#### Step 5: Start the Application

**Development mode (with auto-reload):**
```bash
npm run dev
```

**Production mode:**
```bash
npm start
```

#### Step 6: Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

## Testing

### Running Tests

Make sure MongoDB is running, then:

```bash
npm test
```

Tests will use a separate test database (`ufix_test`) to avoid affecting your development data.

### Manual Testing Flow

1. **Register a Customer:**
   - Go to http://localhost:3000
   - Click "Register"
   - Select "Customer" as user type
   - Fill in the form and submit

2. **Register a Handyman:**
   - Open a new incognito/private window
   - Go to http://localhost:3000
   - Click "Register"
   - Select "Handyman" as user type
   - Add skills (e.g., "plumbing, electrical")
   - Fill in the form and submit

3. **Post a Repair Request (as Customer):**
   - Title: "Fix leaking faucet"
   - Description: "Kitchen faucet is dripping"
   - Category: Plumbing
   - Urgency: ASAP
   - Budget: $50 - $150
   - Add location details
   - Submit

4. **View Available Jobs (as Handyman):**
   - In the handyman window, you should see the repair request
   - Click "Make an Offer"
   - Enter price: $100
   - Duration: "2 hours"
   - Add message (optional)
   - Submit

5. **Accept an Offer (as Customer):**
   - In the customer window, click "View Offers"
   - See the handyman's offer
   - Click "Accept"
   - Request status changes to "In Progress"

6. **Complete Job (as Customer):**
   - Click "Mark as Completed"
   - Request status changes to "Completed"
   - Handyman's completed jobs count increases

## API Testing with cURL

### Register a Customer
```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "phone": "+1234567890",
    "userType": "customer",
    "location": {
      "type": "Point",
      "coordinates": [-74.0060, 40.7128],
      "address": "123 Main St, New York, NY"
    }
  }'
```

### Login
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

### Create Repair Request
```bash
curl -X POST http://localhost:3000/api/repair-requests \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "title": "Fix leaking faucet",
    "description": "Kitchen faucet is leaking",
    "category": "plumbing",
    "location": {
      "type": "Point",
      "coordinates": [-74.0060, 40.7128],
      "address": "123 Main St, New York, NY"
    },
    "urgency": "asap",
    "budget": {
      "min": 50,
      "max": 150
    }
  }'
```

## Troubleshooting

### MongoDB Connection Issues

**Error: "MongoServerError: connect ECONNREFUSED"**
- Make sure MongoDB is running: `sudo systemctl status mongod`
- Start MongoDB if not running: `sudo systemctl start mongod`

**Error: "Authentication failed"**
- Check your MONGODB_URI in .env
- Ensure MongoDB is accessible

### Port Already in Use

**Error: "EADDRINUSE: address already in use :::3000"**
- Change the PORT in .env to a different value
- Or kill the process using port 3000:
  ```bash
  # Find the process
  lsof -i :3000
  # Kill it
  kill -9 <PID>
  ```

### Module Not Found

**Error: "Cannot find module 'express'"**
- Run `npm install` to install all dependencies

## Development Tips

1. **Hot Reload**: Use `npm run dev` for automatic server restart on file changes

2. **Database GUI**: Install MongoDB Compass for a visual interface to your database
   - Download from: https://www.mongodb.com/products/compass

3. **API Testing**: Use Postman or Insomnia for easier API testing
   - Import the API endpoints from the README

4. **Logs**: Check server logs in the console for debugging

5. **Clear Test Data**: To reset your database:
   ```bash
   mongosh
   use ufix
   db.dropDatabase()
   ```

## Production Deployment

For production deployment:

1. Use a managed MongoDB service (MongoDB Atlas, AWS DocumentDB, etc.)
2. Set strong JWT_SECRET
3. Enable HTTPS
4. Set NODE_ENV=production
5. Use a process manager like PM2
6. Set up proper logging
7. Configure CORS appropriately
8. Add rate limiting
9. Implement proper error handling
10. Set up monitoring and alerts

Example PM2 deployment:
```bash
npm install -g pm2
pm2 start server.js --name ufix
pm2 save
pm2 startup
```

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/ido16699-optic/UFIX/issues
- Email: support@ufix.example.com
