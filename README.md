# UFIX - Uber for Handymen

A modern MVP platform that connects customers who need home repairs with skilled handymen in their area. Built with flexibility in mind, allowing customers to post repair requests and receive offers from nearby handymen, choosing the best one for immediate or scheduled service.

## Features

### For Customers
- **Post Repair Requests**: Create detailed repair requests with title, description, category, location, and budget
- **Flexible Scheduling**: Choose between ASAP service or schedule for a specific date/time
- **Receive Multiple Offers**: Get offers from multiple handymen with pricing and estimated duration
- **Choose Your Handyman**: Review handyman profiles, ratings, and completed jobs before selecting
- **Track Progress**: Monitor the status of your repair requests from posting to completion

### For Handymen
- **Find Jobs Nearby**: Automatically see repair requests in your area based on your location
- **Submit Offers**: Make competitive offers with your pricing and estimated duration
- **Build Reputation**: Complete jobs to increase your rating and completed jobs count
- **Manage Offers**: Track all your submitted offers and their status

### Core Features
- User authentication (registration and login) for both customers and handymen
- Location-based matching using geospatial queries
- Real-time offer management
- Job status tracking (open, in_progress, completed, cancelled)
- Responsive web interface

## Technology Stack

### Backend
- **Node.js** with **Express.js** - RESTful API server
- **MongoDB** with **Mongoose** - Database and ODM
- **JWT** - Authentication
- **bcryptjs** - Password hashing

### Frontend
- **Vanilla JavaScript** - Client-side logic
- **HTML5/CSS3** - Responsive UI
- **Fetch API** - HTTP requests

## Getting Started

### Prerequisites
- Node.js (v14 or higher)
- MongoDB (v4.4 or higher)
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ido16699-optic/UFIX.git
cd UFIX
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` and configure:
- `MONGODB_URI`: Your MongoDB connection string
- `JWT_SECRET`: A secure random string for JWT signing
- `PORT`: Server port (default: 3000)

4. Start MongoDB:
```bash
# On macOS/Linux
sudo systemctl start mongodb
# or
mongod

# On Windows
net start MongoDB
```

5. Run the application:

**Development mode:**
```bash
npm run dev
```

**Production mode:**
```bash
npm start
```

6. Open your browser and navigate to:
```
http://localhost:3000
```

## API Documentation

### Authentication

#### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "phone": "+1234567890",
  "userType": "customer", // or "handyman"
  "location": {
    "type": "Point",
    "coordinates": [-74.0060, 40.7128], // [longitude, latitude]
    "address": "123 Main St, New York, NY"
  },
  "skills": ["plumbing", "electrical"] // Only for handymen
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123"
}
```

### Repair Requests

#### Create Repair Request
```http
POST /api/repair-requests
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Fix leaking faucet",
  "description": "Kitchen faucet is leaking",
  "category": "plumbing",
  "location": {
    "type": "Point",
    "coordinates": [-74.0060, 40.7128],
    "address": "123 Main St, New York, NY"
  },
  "urgency": "asap", // or "scheduled"
  "scheduledDate": "2026-02-01T10:00:00Z", // Optional, for scheduled
  "budget": {
    "min": 50,
    "max": 150
  }
}
```

#### Get Repair Requests
```http
GET /api/repair-requests
Authorization: Bearer <token>
```

#### Get Specific Repair Request with Offers
```http
GET /api/repair-requests/:id
Authorization: Bearer <token>
```

#### Accept an Offer
```http
POST /api/repair-requests/:id/accept-offer
Authorization: Bearer <token>
Content-Type: application/json

{
  "offerId": "offer_id_here"
}
```

#### Update Status
```http
PATCH /api/repair-requests/:id/status
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "completed" // or "cancelled"
}
```

### Offers

#### Create Offer (Handyman only)
```http
POST /api/offers
Authorization: Bearer <token>
Content-Type: application/json

{
  "repairRequestId": "request_id_here",
  "price": 100,
  "estimatedDuration": "2 hours",
  "message": "I have 5 years of experience in plumbing"
}
```

#### Get My Offers (Handyman only)
```http
GET /api/offers/my-offers
Authorization: Bearer <token>
```

#### Update Offer (Handyman only)
```http
PATCH /api/offers/:id
Authorization: Bearer <token>
Content-Type: application/json

{
  "price": 120,
  "estimatedDuration": "2.5 hours",
  "message": "Updated estimate"
}
```

## Database Schema

### User
- name: String
- email: String (unique)
- password: String (hashed)
- phone: String
- userType: String (customer/handyman)
- location: GeoJSON Point
- skills: Array of Strings (for handymen)
- rating: Number
- completedJobs: Number

### RepairRequest
- customer: ObjectId (ref: User)
- title: String
- description: String
- category: String (plumbing/electrical/carpentry/painting/general/other)
- location: GeoJSON Point
- urgency: String (asap/scheduled)
- scheduledDate: Date
- budget: { min: Number, max: Number }
- images: Array of Strings
- status: String (open/in_progress/completed/cancelled)
- selectedOffer: ObjectId (ref: Offer)

### Offer
- repairRequest: ObjectId (ref: RepairRequest)
- handyman: ObjectId (ref: User)
- price: Number
- estimatedDuration: String
- message: String
- status: String (pending/accepted/rejected)

## User Flow

### Customer Journey
1. Register/Login as a customer
2. Post a repair request with details
3. Wait for offers from nearby handymen
4. Review offers and handyman profiles
5. Accept the best offer
6. Mark the job as completed when done

### Handyman Journey
1. Register/Login as a handyman
2. Browse available repair requests nearby
3. Submit offers with pricing and timeline
4. Wait for customer to accept
5. Complete the job and build reputation

## Project Structure

```
UFIX/
├── backend/
│   ├── config/
│   │   └── database.js       # MongoDB connection
│   ├── middleware/
│   │   └── auth.js           # Authentication middleware
│   ├── models/
│   │   ├── User.js           # User model
│   │   ├── RepairRequest.js  # Repair request model
│   │   └── Offer.js          # Offer model
│   └── routes/
│       ├── auth.js           # Authentication routes
│       ├── repairRequests.js # Repair request routes
│       └── offers.js         # Offer routes
├── public/
│   ├── index.html            # Main HTML file
│   ├── styles.css            # Styles
│   └── app.js                # Frontend JavaScript
├── server.js                 # Main server file
├── package.json              # Dependencies
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Security Features

- Password hashing with bcryptjs
- JWT-based authentication
- Protected API routes
- User type verification (customer/handyman)
- Input validation

## Future Enhancements

- Real-time notifications
- Image upload for repair requests
- Payment integration
- Rating and review system
- Chat functionality between customers and handymen
- Mobile app (iOS/Android)
- Advanced search and filters
- Email notifications
- SMS notifications
- In-app messaging
- Calendar integration
- Multi-language support

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

ISC

## Support

For issues or questions, please open an issue on GitHub.
