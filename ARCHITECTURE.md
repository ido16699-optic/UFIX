# UFIX Platform Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────┐         ┌──────────────────────┐       │
│  │   Customer Web UI   │         │  Handyman Web UI     │       │
│  │  - Post Requests    │         │  - Browse Jobs       │       │
│  │  - View Offers      │         │  - Submit Offers     │       │
│  │  - Accept Offers    │         │  - Track Offers      │       │
│  └──────────┬──────────┘         └──────────┬───────────┘       │
│             │                               │                    │
│             └───────────────┬───────────────┘                    │
│                             │                                    │
│                    ┌────────▼─────────┐                          │
│                    │   Frontend JS    │                          │
│                    │  - Fetch API     │                          │
│                    │  - JWT Storage   │                          │
│                    │  - State Mgmt    │                          │
│                    └────────┬─────────┘                          │
└─────────────────────────────┼──────────────────────────────────┘
                              │
                              │ HTTPS/JSON
                              │
┌─────────────────────────────▼──────────────────────────────────┐
│                      API LAYER (Express.js)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Middleware                             │   │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌──────────────┐   │   │
│  │  │  CORS  │  │  Body  │  │  Auth  │  │ Role Check   │   │   │
│  │  │        │─▶│ Parser │─▶│  JWT   │─▶│ Customer/    │   │   │
│  │  │        │  │        │  │        │  │ Handyman     │   │   │
│  │  └────────┘  └────────┘  └────────┘  └──────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Route Handlers                           │   │
│  │  ┌─────────────┐  ┌────────────┐  ┌─────────────────┐   │   │
│  │  │    Auth     │  │  Repair    │  │     Offers      │   │   │
│  │  │             │  │  Requests  │  │                 │   │   │
│  │  │ - Register  │  │ - Create   │  │ - Create        │   │   │
│  │  │ - Login     │  │ - List     │  │ - List          │   │   │
│  │  │             │  │ - Get      │  │ - Update        │   │   │
│  │  │             │  │ - Accept   │  │                 │   │   │
│  │  │             │  │ - Update   │  │                 │   │   │
│  │  └─────────────┘  └────────────┘  └─────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              │ Mongoose ODM
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                    DATABASE LAYER (MongoDB)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Users        │  │ Repair       │  │ Offers               │  │
│  │ Collection   │  │ Requests     │  │ Collection           │  │
│  │              │  │ Collection   │  │                      │  │
│  │ - Customers  │  │              │  │ - Price              │  │
│  │ - Handymen   │  │ - Title      │  │ - Duration           │  │
│  │ - Location   │  │ - Description│  │ - Message            │  │
│  │   (GeoJSON)  │  │ - Location   │  │ - Status             │  │
│  │ - Skills     │  │   (GeoJSON)  │  │ - References:        │  │
│  │ - Rating     │  │ - Status     │  │   * Request          │  │
│  │              │  │ - Urgency    │  │   * Handyman         │  │
│  │ Indexes:     │  │              │  │                      │  │
│  │ - Email      │  │ Indexes:     │  │                      │  │
│  │ - Location   │  │ - Location   │  │                      │  │
│  │   (2dsphere) │  │   (2dsphere) │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### Customer Flow: Post Repair Request

```
Customer → Frontend → API → Database → API → Frontend → Customer
  |          |         |        |        |       |          |
  |          |         |        |        |       |          |
  1. Fill    2. POST   3. Auth  4. Save  5. Return Success  6. Display
     Form       /api/     Check    Request   New Request      Confirmation
              repair-    JWT      to DB     with ID
              requests
```

### Handyman Flow: Browse & Offer

```
Handyman → Frontend → API → Database → API → Frontend → Handyman
   |          |        |        |        |       |           |
   |          |        |        |        |       |           |
   1. View    2. GET   3. Auth  4. Geo-  5. Return Nearby   6. See Jobs
      Jobs      /api/     Check   spatial  Requests List       & Submit
             repair-    JWT     Query    Filtered            Offers
             requests           by       by Status
                               Location  & Proximity
```

### Accept Offer Flow

```
Customer → Frontend → API → Database Operations → API → Frontend
   |          |        |              |              |       |
   |          |        |              |              |       |
   1. Select  2. POST  3. Verify      4. Update:     5. Return Updated
      Offer     /api/    Customer        - Offer → Accepted     Data
              repair-   Owns Request     - Other Offers → Rejected
              requests/                  - Request → In Progress
              :id/accept-offer           - Set selectedOffer
```

## Component Interaction

```
┌────────────────────────────────────────────────────────────────┐
│                    Authentication Flow                          │
└────────────────────────────────────────────────────────────────┘

User Input (Email/Password)
         │
         ▼
    Frontend Validation
         │
         ▼
    POST /api/auth/login
         │
         ▼
    Backend: Find User by Email
         │
         ▼
    bcrypt.compare(password)
         │
    ┌────┴────┐
    │         │
    ✓         ✗
    │         │
    │         ▼
    │    401 Error
    │
    ▼
Generate JWT Token
    │
    ▼
Return Token + User Info
    │
    ▼
Frontend: Store Token
    │
    ▼
Include in Future Requests
(Authorization: Bearer <token>)
```

## Location-Based Matching

```
┌────────────────────────────────────────────────────────────────┐
│              Geospatial Query Process                           │
└────────────────────────────────────────────────────────────────┘

Handyman Logs In
      │
      ▼
System Retrieves Handyman Location
      │
      ▼
Handyman Requests Available Jobs
      │
      ▼
Backend Constructs Geo Query:
      │
      ├─ Find RepairRequests WHERE:
      │  ├─ status = 'open'
      │  └─ location NEAR handyman.location
      │     WITHIN 50km (50000 meters)
      │
      ▼
MongoDB 2dsphere Index:
      │
      ├─ Calculates distances
      ├─ Filters by radius
      └─ Returns sorted by proximity
      │
      ▼
API Returns Filtered Jobs
      │
      ▼
Frontend Displays Job Cards
```

## Security Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    Security Layers                              │
└────────────────────────────────────────────────────────────────┘

1. Transport Layer
   ├─ HTTPS (Production)
   └─ CORS Configuration

2. Authentication Layer
   ├─ Password Hashing (bcryptjs, 10 rounds)
   ├─ JWT Tokens (7-day expiry)
   └─ Secure Secret (Environment Variable)

3. Authorization Layer
   ├─ Auth Middleware (Token Validation)
   ├─ User Type Check (Customer/Handyman)
   └─ Resource Ownership Verification

4. Data Layer
   ├─ MongoDB Security (Connection String)
   ├─ Input Validation
   └─ SQL Injection Prevention (NoSQL)

5. Application Layer
   ├─ Environment Variables (.env)
   ├─ No Secrets in Code
   └─ Error Handling (No Info Leakage)
```

## Deployment Architecture (Docker)

```
┌────────────────────────────────────────────────────────────────┐
│                Docker Compose Environment                       │
└────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │  Docker Host        │
                    │                     │
                    │  ┌───────────────┐  │
                    │  │ Bridge        │  │
                    │  │ Network       │  │
                    │  │ (ufix-network)│  │
                    │  └───────┬───────┘  │
                    │          │          │
        ┌───────────┼──────────┼──────────┼──────────┐
        │           │          │          │          │
        │  ┌────────▼──────┐ ┌▼──────────▼─────┐   │
        │  │ UFIX App      │ │ MongoDB         │   │
        │  │ Container     │ │ Container       │   │
        │  │               │ │                 │   │
        │  │ Port: 3000 ───┼─┼─▶ Exposed      │   │
        │  │               │ │                 │   │
        │  │ Health Check  │ │ Port: 27017    │   │
        │  │ /api/health   │ │                 │   │
        │  │               │ │ Volume:         │   │
        │  │ Restart:      │ │ mongodb_data    │   │
        │  │ unless-stopped│ │                 │   │
        │  └───────────────┘ └─────────────────┘   │
        │                                            │
        └────────────────────────────────────────────┘
                    │
                    │ Port Mapping
                    │
        ┌───────────▼──────────┐
        │  Host Machine        │
        │  localhost:3000 ─────┼─▶ Browser Access
        └──────────────────────┘
```

## Technology Stack Layers

```
┌────────────────────────────────────────────────────────────────┐
│                    Technology Stack                             │
└────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Presentation Layer                                          │
│ - HTML5, CSS3, JavaScript (ES6+)                           │
│ - Responsive Design, Modal Dialogs, Form Validation        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ API Layer                                                   │
│ - Express.js 5.x (Web Framework)                           │
│ - CORS, Body Parser, JWT Middleware                        │
│ - RESTful Endpoints, JSON Responses                        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Business Logic Layer                                        │
│ - User Authentication (bcryptjs, JWT)                       │
│ - Geospatial Matching (MongoDB $near queries)              │
│ - Offer Management (Status transitions)                    │
│ - Role-Based Access Control                                │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Data Access Layer                                           │
│ - Mongoose 9.x (ODM)                                        │
│ - Schema Validation, Middleware Hooks                      │
│ - Population, Indexing                                      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Database Layer                                              │
│ - MongoDB 6.x (NoSQL Database)                             │
│ - Collections: Users, RepairRequests, Offers               │
│ - Indexes: 2dsphere (location), unique (email)             │
└─────────────────────────────────────────────────────────────┘
```

## Request Lifecycle

```
1. HTTP Request Arrives
        │
        ▼
2. CORS Middleware
   ├─ Check Origin
   └─ Set Headers
        │
        ▼
3. Body Parser
   ├─ Parse JSON
   └─ Validate Content-Type
        │
        ▼
4. Route Matching
   └─ Express Router
        │
        ▼
5. Authentication (if protected)
   ├─ Extract JWT from header
   ├─ Verify signature
   ├─ Check expiry
   └─ Attach user info to req
        │
        ▼
6. Authorization (if role-specific)
   └─ Check user type
        │
        ▼
7. Controller Logic
   ├─ Validate input
   ├─ Business logic
   └─ Database operations
        │
        ▼
8. Response
   ├─ Format JSON
   ├─ Set status code
   └─ Send response
        │
        ▼
9. Error Handling (if error)
   └─ Catch & format error
```

---

**Last Updated**: January 28, 2026  
**Platform**: UFIX - Uber for Handymen  
**Version**: 1.0.0 (MVP)
