# UFIX Platform Features

## Overview
UFIX is an MVP platform that connects customers needing home repairs with skilled handymen. The platform prioritizes flexibility, allowing customers to post requests and receive competitive offers from nearby professionals.

## Core User Flows

### 1. Customer Flow

#### A. Registration & Login
- **Register**: Create an account with name, email, password, phone, and location
- **Login**: Authenticate using email and password
- **Session**: Receive JWT token valid for 7 days

#### B. Post Repair Request
**Fields:**
- **Title**: Brief description (e.g., "Fix leaking faucet")
- **Description**: Detailed explanation of the issue
- **Category**: 
  - Plumbing
  - Electrical
  - Carpentry
  - Painting
  - General
  - Other
- **Location**: 
  - Address (text)
  - Coordinates (latitude/longitude for geospatial matching)
- **Urgency**:
  - **ASAP**: Immediate service required
  - **Scheduled**: Service needed at a specific date/time
- **Budget**: Optional min/max price range
- **Images**: Optional photos (placeholder for future implementation)

**Status Progression:**
1. **Open**: Accepting offers from handymen
2. **In Progress**: Offer accepted, work ongoing
3. **Completed**: Job finished successfully
4. **Cancelled**: Request cancelled by customer

#### C. Receive & Review Offers
- View all offers for a repair request
- See handyman details:
  - Name
  - Rating (0-5 stars)
  - Completed jobs count
  - Skills/expertise
- Compare offers:
  - Price
  - Estimated duration
  - Personal message from handyman

#### D. Accept Offer & Manage Job
- Accept the best offer
- Automatically reject other offers
- Request moves to "In Progress"
- Mark job as completed when finished
- Handyman's stats updated (completed jobs count)

### 2. Handyman Flow

#### A. Registration & Login
- **Register**: Create account with additional fields:
  - Skills (array): e.g., ["plumbing", "electrical", "carpentry"]
  - Location for proximity matching
- **Login**: Same as customers

#### B. Browse Available Jobs
- **Automatic Filtering**:
  - Only open requests shown
  - Proximity-based (within 50km radius by default)
  - Sorted by creation date
- **Job Details Visible**:
  - Title and description
  - Category
  - Urgency (ASAP or scheduled date)
  - Budget range (if specified)
  - Location/address
  - Customer name and rating

#### C. Submit Offers
**Offer Fields:**
- **Price**: Your quoted price for the job
- **Estimated Duration**: How long the job will take (e.g., "2 hours", "1 day")
- **Message**: Optional personalized message to customer

**Offer States:**
- **Pending**: Waiting for customer decision
- **Accepted**: Customer accepted your offer
- **Rejected**: Customer chose another handyman

**Business Rules:**
- One offer per handyman per request
- Can only offer on open requests
- Can update pending offers

#### D. Track Offers
- View all submitted offers
- See offer status (pending/accepted/rejected)
- Access job details for accepted offers
- Build reputation through completed jobs

## Technical Features

### 1. Location-Based Matching
- **Geospatial Queries**: MongoDB 2dsphere indexes
- **Proximity Search**: Find requests within radius
- **Coordinates**: Standard GeoJSON format [longitude, latitude]
- **Default Radius**: 50km (configurable)

### 2. Authentication & Security
- **Password Hashing**: bcryptjs with salt rounds
- **JWT Tokens**: Secure, stateless authentication
- **Token Expiry**: 7 days
- **Protected Routes**: Middleware-based authorization
- **User Type Verification**: Customer vs Handyman access control

### 3. Real-Time Status Updates
- Request status changes reflected immediately
- Offer acceptance triggers multiple updates:
  - Selected offer → accepted
  - Other offers → rejected
  - Request → in_progress
- Completion updates handyman statistics

### 4. Database Models

#### User Model
```javascript
{
  name: String,
  email: String (unique, indexed),
  password: String (hashed),
  phone: String,
  userType: "customer" | "handyman",
  location: {
    type: "Point",
    coordinates: [longitude, latitude],
    address: String
  },
  skills: [String], // handymen only
  rating: Number (0-5),
  completedJobs: Number,
  createdAt: Date
}
```

#### RepairRequest Model
```javascript
{
  customer: ObjectId (ref: User),
  title: String,
  description: String,
  category: "plumbing" | "electrical" | "carpentry" | "painting" | "general" | "other",
  location: GeoJSON Point,
  urgency: "asap" | "scheduled",
  scheduledDate: Date (optional),
  budget: { min: Number, max: Number },
  images: [String],
  status: "open" | "in_progress" | "completed" | "cancelled",
  selectedOffer: ObjectId (ref: Offer),
  createdAt: Date,
  updatedAt: Date
}
```

#### Offer Model
```javascript
{
  repairRequest: ObjectId (ref: RepairRequest),
  handyman: ObjectId (ref: User),
  price: Number,
  estimatedDuration: String,
  message: String,
  status: "pending" | "accepted" | "rejected",
  createdAt: Date
}
```

### 5. API Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

#### Repair Requests
- `POST /api/repair-requests` - Create request (customer only)
- `GET /api/repair-requests` - List requests (filtered by user type)
- `GET /api/repair-requests/:id` - Get request with offers
- `POST /api/repair-requests/:id/accept-offer` - Accept offer (customer only)
- `PATCH /api/repair-requests/:id/status` - Update status

#### Offers
- `POST /api/offers` - Create offer (handyman only)
- `GET /api/offers/my-offers` - List my offers (handyman only)
- `PATCH /api/offers/:id` - Update offer (handyman only)

#### System
- `GET /api/health` - Health check

## User Interface Features

### Design Principles
- **Responsive**: Works on desktop, tablet, and mobile
- **Intuitive**: Clear user flows with minimal clicks
- **Visual Feedback**: Status badges, color coding
- **Modal Dialogs**: For offer viewing and selection

### Customer Dashboard
1. **Request Form**: Quick and easy repair request creation
2. **My Requests**: List of all posted requests
3. **Status Badges**: Visual indicators (open, in progress, completed)
4. **View Offers Button**: Access offers for open requests
5. **Offer Comparison**: Side-by-side handyman profiles

### Handyman Dashboard
1. **Available Jobs**: Card-based layout of nearby requests
2. **Quick Offer**: Inline offer submission
3. **My Offers**: Tracking all submitted offers
4. **Status Indicators**: Pending, accepted, rejected badges
5. **Job Details**: Full request information before offering

### Visual Elements
- **Color Coding**:
  - Green: Open, Accepted, Completed
  - Orange: In Progress
  - Yellow: Pending
  - Red: ASAP, Rejected, Cancelled
  - Blue: Scheduled, Completed
- **Badges**: Pill-shaped status indicators
- **Cards**: Shadowed containers for requests/offers
- **Forms**: Clean, organized input fields
- **Buttons**: Gradient hover effects

## Business Logic

### Offer Acceptance Flow
1. Customer clicks "Accept" on an offer
2. System verifies:
   - Customer owns the request
   - Offer exists and is pending
   - Request is still open
3. Updates:
   - Selected offer status → accepted
   - All other offers → rejected
   - Request status → in_progress
   - Request selectedOffer → offer ID
4. Returns updated request and offer

### Job Completion Flow
1. Customer marks request as completed
2. System:
   - Updates request status → completed
   - Increments handyman's completedJobs count
3. Used for handyman reputation building

### Proximity Matching
```javascript
// Find requests within 50km of handyman
{
  location: {
    $near: {
      $geometry: {
        type: "Point",
        coordinates: [handymanLng, handymanLat]
      },
      $maxDistance: 50000 // meters
    }
  }
}
```

## Future Enhancement Ideas

### High Priority
1. **Rating System**: Allow customers to rate handymen after completion
2. **Image Upload**: Support for repair request photos
3. **Push Notifications**: Real-time alerts for new requests/offers
4. **In-App Messaging**: Direct communication between parties
5. **Payment Integration**: Secure payment processing (Stripe, PayPal)

### Medium Priority
6. **Advanced Search**: Filter by category, price range, date
7. **Calendar Integration**: Schedule management
8. **Email Notifications**: Updates via email
9. **SMS Alerts**: Text message notifications
10. **Reviews & Comments**: Detailed feedback system

### Low Priority
11. **Mobile Apps**: Native iOS and Android apps
12. **Admin Dashboard**: Platform management
13. **Analytics**: Usage statistics and insights
14. **Multi-language**: Internationalization
15. **Advanced Matching**: AI-based handyman suggestions

## Performance Considerations

### Database Optimization
- **Indexes**: 
  - Email (unique)
  - Location (2dsphere for geospatial queries)
  - Status fields for filtering
- **Population**: Selective field population to reduce data transfer
- **Pagination**: Support for large datasets (implemented in API, ready for frontend)

### Security Best Practices
- **Password Hashing**: Never store plain text passwords
- **JWT Secret**: Environment variable, never committed
- **Input Validation**: Server-side validation for all inputs
- **CORS**: Configurable origins
- **Rate Limiting**: Ready for implementation
- **HTTPS**: Recommended for production

### Scalability
- **Stateless API**: JWT-based, horizontally scalable
- **Database**: MongoDB, designed for scaling
- **Docker**: Container-ready for cloud deployment
- **Environment Config**: 12-factor app principles

## Testing Strategy

### Unit Tests
- User model password hashing
- Authentication middleware
- Geospatial query construction

### Integration Tests
- Registration and login flows
- Request creation and retrieval
- Offer submission and acceptance
- Status updates

### End-to-End Tests
- Complete customer journey
- Complete handyman journey
- Multi-user scenarios

## Deployment Architecture

### Development
```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
┌──────▼──────┐
│  Node.js    │
│  (port 3000)│
└──────┬──────┘
       │
┌──────▼──────┐
│  MongoDB    │
│(port 27017) │
└─────────────┘
```

### Production (Docker)
```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
┌──────▼──────────┐
│  Docker Bridge  │
│    Network      │
├─────────────────┤
│                 │
│  ┌───────────┐  │
│  │   UFIX    │  │
│  │    App    │  │
│  │ Container │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │  MongoDB  │  │
│  │ Container │  │
│  └───────────┘  │
└─────────────────┘
```

## Support & Maintenance

### Monitoring
- Health check endpoint: `/api/health`
- Docker health checks
- Log aggregation recommended

### Backup Strategy
- Regular MongoDB backups
- Environment variable backups
- Code versioning (Git)

### Updates
- Rolling updates with zero downtime
- Database migrations (when needed)
- API versioning (future consideration)

---

**Last Updated**: January 28, 2026
**Version**: 1.0.0 (MVP)
**Platform**: UFIX - Uber for Handymen
