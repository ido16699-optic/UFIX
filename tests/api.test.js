const request = require('supertest');
const mongoose = require('mongoose');
const app = require('../server');
const User = require('../backend/models/User');
const RepairRequest = require('../backend/models/RepairRequest');
const Offer = require('../backend/models/Offer');

// Test database URI
const TEST_DB_URI = 'mongodb://localhost:27017/ufix_test';

// Test user credentials
const testCustomer = {
  name: 'Test Customer',
  email: 'customer@test.com',
  password: 'password123',
  phone: '+1234567890',
  userType: 'customer',
  location: {
    type: 'Point',
    coordinates: [-74.0060, 40.7128],
    address: '123 Test St, New York, NY'
  }
};

const testHandyman = {
  name: 'Test Handyman',
  email: 'handyman@test.com',
  password: 'password123',
  phone: '+0987654321',
  userType: 'handyman',
  location: {
    type: 'Point',
    coordinates: [-74.0050, 40.7130],
    address: '456 Test Ave, New York, NY'
  },
  skills: ['plumbing', 'electrical']
};

let customerToken, handymanToken, repairRequestId, offerId;

// Connect to test database before all tests
beforeAll(async () => {
  await mongoose.connect(TEST_DB_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true
  });
});

// Clean up database after each test
afterEach(async () => {
  await User.deleteMany({});
  await RepairRequest.deleteMany({});
  await Offer.deleteMany({});
});

// Disconnect after all tests
afterAll(async () => {
  await mongoose.connection.close();
});

describe('Authentication', () => {
  test('should register a new customer', async () => {
    const response = await request(app)
      .post('/api/auth/register')
      .send(testCustomer)
      .expect(201);

    expect(response.body).toHaveProperty('token');
    expect(response.body.user.email).toBe(testCustomer.email);
    expect(response.body.user.userType).toBe('customer');
  });

  test('should register a new handyman', async () => {
    const response = await request(app)
      .post('/api/auth/register')
      .send(testHandyman)
      .expect(201);

    expect(response.body).toHaveProperty('token');
    expect(response.body.user.email).toBe(testHandyman.email);
    expect(response.body.user.userType).toBe('handyman');
  });

  test('should not register user with existing email', async () => {
    await request(app)
      .post('/api/auth/register')
      .send(testCustomer);

    const response = await request(app)
      .post('/api/auth/register')
      .send(testCustomer)
      .expect(400);

    expect(response.body.error).toContain('already registered');
  });

  test('should login existing user', async () => {
    await request(app)
      .post('/api/auth/register')
      .send(testCustomer);

    const response = await request(app)
      .post('/api/auth/login')
      .send({
        email: testCustomer.email,
        password: testCustomer.password
      })
      .expect(200);

    expect(response.body).toHaveProperty('token');
    expect(response.body.user.email).toBe(testCustomer.email);
  });

  test('should not login with wrong password', async () => {
    await request(app)
      .post('/api/auth/register')
      .send(testCustomer);

    await request(app)
      .post('/api/auth/login')
      .send({
        email: testCustomer.email,
        password: 'wrongpassword'
      })
      .expect(401);
  });
});

describe('Repair Requests', () => {
  beforeEach(async () => {
    // Register and login customer
    const customerResponse = await request(app)
      .post('/api/auth/register')
      .send(testCustomer);
    customerToken = customerResponse.body.token;

    // Register and login handyman
    const handymanResponse = await request(app)
      .post('/api/auth/register')
      .send(testHandyman);
    handymanToken = handymanResponse.body.token;
  });

  test('should create a repair request as customer', async () => {
    const repairRequest = {
      title: 'Fix leaking faucet',
      description: 'Kitchen faucet is leaking',
      category: 'plumbing',
      location: {
        type: 'Point',
        coordinates: [-74.0060, 40.7128],
        address: '123 Test St, New York, NY'
      },
      urgency: 'asap',
      budget: {
        min: 50,
        max: 150
      }
    };

    const response = await request(app)
      .post('/api/repair-requests')
      .set('Authorization', `Bearer ${customerToken}`)
      .send(repairRequest)
      .expect(201);

    expect(response.body.repairRequest.title).toBe(repairRequest.title);
    expect(response.body.repairRequest.status).toBe('open');
    repairRequestId = response.body.repairRequest._id;
  });

  test('should not create repair request without authentication', async () => {
    const repairRequest = {
      title: 'Fix leaking faucet',
      description: 'Kitchen faucet is leaking',
      category: 'plumbing',
      location: {
        type: 'Point',
        coordinates: [-74.0060, 40.7128],
        address: '123 Test St, New York, NY'
      },
      urgency: 'asap'
    };

    await request(app)
      .post('/api/repair-requests')
      .send(repairRequest)
      .expect(401);
  });

  test('should get repair requests as customer', async () => {
    // Create a repair request first
    const repairRequest = {
      title: 'Fix leaking faucet',
      description: 'Kitchen faucet is leaking',
      category: 'plumbing',
      location: {
        type: 'Point',
        coordinates: [-74.0060, 40.7128],
        address: '123 Test St, New York, NY'
      },
      urgency: 'asap'
    };

    await request(app)
      .post('/api/repair-requests')
      .set('Authorization', `Bearer ${customerToken}`)
      .send(repairRequest);

    const response = await request(app)
      .get('/api/repair-requests')
      .set('Authorization', `Bearer ${customerToken}`)
      .expect(200);

    expect(response.body.repairRequests).toHaveLength(1);
    expect(response.body.repairRequests[0].title).toBe(repairRequest.title);
  });

  test('should get nearby repair requests as handyman', async () => {
    // Create a repair request as customer
    const repairRequest = {
      title: 'Fix leaking faucet',
      description: 'Kitchen faucet is leaking',
      category: 'plumbing',
      location: {
        type: 'Point',
        coordinates: [-74.0060, 40.7128],
        address: '123 Test St, New York, NY'
      },
      urgency: 'asap'
    };

    await request(app)
      .post('/api/repair-requests')
      .set('Authorization', `Bearer ${customerToken}`)
      .send(repairRequest);

    // Get requests as handyman
    const response = await request(app)
      .get('/api/repair-requests')
      .set('Authorization', `Bearer ${handymanToken}`)
      .expect(200);

    expect(response.body.repairRequests).toHaveLength(1);
    expect(response.body.repairRequests[0].status).toBe('open');
  });
});

describe('Offers', () => {
  beforeEach(async () => {
    // Register users
    const customerResponse = await request(app)
      .post('/api/auth/register')
      .send(testCustomer);
    customerToken = customerResponse.body.token;

    const handymanResponse = await request(app)
      .post('/api/auth/register')
      .send(testHandyman);
    handymanToken = handymanResponse.body.token;

    // Create a repair request
    const repairRequest = {
      title: 'Fix leaking faucet',
      description: 'Kitchen faucet is leaking',
      category: 'plumbing',
      location: {
        type: 'Point',
        coordinates: [-74.0060, 40.7128],
        address: '123 Test St, New York, NY'
      },
      urgency: 'asap'
    };

    const requestResponse = await request(app)
      .post('/api/repair-requests')
      .set('Authorization', `Bearer ${customerToken}`)
      .send(repairRequest);

    repairRequestId = requestResponse.body.repairRequest._id;
  });

  test('should create an offer as handyman', async () => {
    const offer = {
      repairRequestId: repairRequestId,
      price: 100,
      estimatedDuration: '2 hours',
      message: 'I have 5 years of experience'
    };

    const response = await request(app)
      .post('/api/offers')
      .set('Authorization', `Bearer ${handymanToken}`)
      .send(offer)
      .expect(201);

    expect(response.body.offer.price).toBe(offer.price);
    expect(response.body.offer.status).toBe('pending');
    offerId = response.body.offer._id;
  });

  test('should not create offer as customer', async () => {
    const offer = {
      repairRequestId: repairRequestId,
      price: 100,
      estimatedDuration: '2 hours'
    };

    await request(app)
      .post('/api/offers')
      .set('Authorization', `Bearer ${customerToken}`)
      .send(offer)
      .expect(403);
  });

  test('should get handyman offers', async () => {
    const offer = {
      repairRequestId: repairRequestId,
      price: 100,
      estimatedDuration: '2 hours',
      message: 'I have 5 years of experience'
    };

    await request(app)
      .post('/api/offers')
      .set('Authorization', `Bearer ${handymanToken}`)
      .send(offer);

    const response = await request(app)
      .get('/api/offers/my-offers')
      .set('Authorization', `Bearer ${handymanToken}`)
      .expect(200);

    expect(response.body.offers).toHaveLength(1);
    expect(response.body.offers[0].price).toBe(offer.price);
  });

  test('should accept an offer as customer', async () => {
    const offer = {
      repairRequestId: repairRequestId,
      price: 100,
      estimatedDuration: '2 hours'
    };

    const offerResponse = await request(app)
      .post('/api/offers')
      .set('Authorization', `Bearer ${handymanToken}`)
      .send(offer);

    offerId = offerResponse.body.offer._id;

    const response = await request(app)
      .post(`/api/repair-requests/${repairRequestId}/accept-offer`)
      .set('Authorization', `Bearer ${customerToken}`)
      .send({ offerId })
      .expect(200);

    expect(response.body.offer.status).toBe('accepted');
    expect(response.body.repairRequest.status).toBe('in_progress');
  });
});

describe('Job Status Updates', () => {
  beforeEach(async () => {
    const customerResponse = await request(app)
      .post('/api/auth/register')
      .send(testCustomer);
    customerToken = customerResponse.body.token;

    const requestResponse = await request(app)
      .post('/api/repair-requests')
      .set('Authorization', `Bearer ${customerToken}`)
      .send({
        title: 'Fix leaking faucet',
        description: 'Kitchen faucet is leaking',
        category: 'plumbing',
        location: {
          type: 'Point',
          coordinates: [-74.0060, 40.7128],
          address: '123 Test St, New York, NY'
        },
        urgency: 'asap'
      });

    repairRequestId = requestResponse.body.repairRequest._id;
  });

  test('should update repair request status', async () => {
    const response = await request(app)
      .patch(`/api/repair-requests/${repairRequestId}/status`)
      .set('Authorization', `Bearer ${customerToken}`)
      .send({ status: 'cancelled' })
      .expect(200);

    expect(response.body.repairRequest.status).toBe('cancelled');
  });
});
