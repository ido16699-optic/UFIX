const API_URL = '/api';
let currentUser = null;
let authToken = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('loginBtn').addEventListener('click', showLogin);
    document.getElementById('registerBtn').addEventListener('click', showRegister);
    document.getElementById('logoutBtn').addEventListener('click', logout);
    
    document.getElementById('loginFormElement').addEventListener('submit', handleLogin);
    document.getElementById('registerFormElement').addEventListener('submit', handleRegister);
    document.getElementById('repairRequestForm').addEventListener('submit', handleCreateRepairRequest);
    
    document.getElementById('registerUserType').addEventListener('change', (e) => {
        const handymanFields = document.getElementById('handymanFields');
        handymanFields.style.display = e.target.value === 'handyman' ? 'block' : 'none';
    });
    
    document.getElementById('requestUrgency').addEventListener('change', (e) => {
        const scheduledField = document.getElementById('scheduledDateField');
        scheduledField.style.display = e.target.value === 'scheduled' ? 'block' : 'none';
    });
}

function checkAuth() {
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('currentUser');
    
    if (token && user) {
        authToken = token;
        currentUser = JSON.parse(user);
        showDashboard();
    } else {
        showLogin();
    }
}

function showLogin() {
    hideAll();
    document.getElementById('loginForm').style.display = 'block';
}

function showRegister() {
    hideAll();
    document.getElementById('registerForm').style.display = 'block';
}

function hideAll() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('customerDashboard').style.display = 'none';
    document.getElementById('handymanDashboard').style.display = 'none';
}

async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            showDashboard();
        } else {
            alert(data.error || 'Login failed');
        }
    } catch (error) {
        alert('Login error: ' + error.message);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const phone = document.getElementById('registerPhone').value;
    const userType = document.getElementById('registerUserType').value;
    const address = document.getElementById('registerAddress').value;
    const lat = parseFloat(document.getElementById('registerLat').value);
    const lng = parseFloat(document.getElementById('registerLng').value);
    
    const userData = {
        name,
        email,
        password,
        phone,
        userType,
        location: {
            type: 'Point',
            coordinates: [lng, lat],
            address
        }
    };
    
    if (userType === 'handyman') {
        const skillsInput = document.getElementById('registerSkills').value;
        userData.skills = skillsInput.split(',').map(s => s.trim()).filter(s => s);
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            showDashboard();
        } else {
            alert(data.error || 'Registration failed');
        }
    } catch (error) {
        alert('Registration error: ' + error.message);
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    showLogin();
}

function showDashboard() {
    hideAll();
    document.getElementById('loginBtn').style.display = 'none';
    document.getElementById('registerBtn').style.display = 'none';
    document.getElementById('logoutBtn').style.display = 'inline-block';
    
    if (currentUser.userType === 'customer') {
        document.getElementById('customerName').textContent = currentUser.name;
        document.getElementById('customerDashboard').style.display = 'block';
        loadCustomerRequests();
    } else {
        document.getElementById('handymanName').textContent = currentUser.name;
        document.getElementById('handymanDashboard').style.display = 'block';
        loadAvailableJobs();
        loadMyOffers();
    }
}

async function handleCreateRepairRequest(e) {
    e.preventDefault();
    
    const title = document.getElementById('requestTitle').value;
    const description = document.getElementById('requestDescription').value;
    const category = document.getElementById('requestCategory').value;
    const urgency = document.getElementById('requestUrgency').value;
    const address = document.getElementById('requestAddress').value;
    const lat = parseFloat(document.getElementById('requestLat').value);
    const lng = parseFloat(document.getElementById('requestLng').value);
    
    const requestData = {
        title,
        description,
        category,
        urgency,
        location: {
            type: 'Point',
            coordinates: [lng, lat],
            address
        }
    };
    
    if (urgency === 'scheduled') {
        requestData.scheduledDate = document.getElementById('requestScheduledDate').value;
    }
    
    const budgetMin = document.getElementById('requestBudgetMin').value;
    const budgetMax = document.getElementById('requestBudgetMax').value;
    if (budgetMin || budgetMax) {
        requestData.budget = {
            min: budgetMin ? parseFloat(budgetMin) : undefined,
            max: budgetMax ? parseFloat(budgetMax) : undefined
        };
    }
    
    try {
        const response = await fetch(`${API_URL}/repair-requests`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Repair request posted successfully!');
            e.target.reset();
            loadCustomerRequests();
        } else {
            alert(data.error || 'Failed to post request');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function loadCustomerRequests() {
    try {
        const response = await fetch(`${API_URL}/repair-requests`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayCustomerRequests(data.repairRequests);
        }
    } catch (error) {
        console.error('Error loading requests:', error);
    }
}

function displayCustomerRequests(requests) {
    const container = document.getElementById('customerRequests');
    
    if (!requests || requests.length === 0) {
        container.innerHTML = '<p>No repair requests yet. Post one above!</p>';
        return;
    }
    
    container.innerHTML = requests.map(req => `
        <div class="request-card">
            <h4>${req.title}</h4>
            <p><strong>Category:</strong> ${req.category}</p>
            <p><strong>Description:</strong> ${req.description}</p>
            <p><strong>Urgency:</strong> <span class="badge ${req.urgency}">${req.urgency}</span></p>
            <p><strong>Status:</strong> <span class="badge ${req.status}">${req.status}</span></p>
            <p><strong>Location:</strong> ${req.location.address}</p>
            ${req.scheduledDate ? `<p><strong>Scheduled:</strong> ${new Date(req.scheduledDate).toLocaleString()}</p>` : ''}
            ${req.budget ? `<p><strong>Budget:</strong> $${req.budget.min || 0} - $${req.budget.max || 0}</p>` : ''}
            <p><strong>Posted:</strong> ${new Date(req.createdAt).toLocaleString()}</p>
            ${req.status === 'open' ? `<button onclick="viewOffers('${req._id}')">View Offers</button>` : ''}
            ${req.status === 'in_progress' ? `<button class="btn-complete" onclick="completeRequest('${req._id}')">Mark as Completed</button>` : ''}
        </div>
    `).join('');
}

async function viewOffers(requestId) {
    try {
        const response = await fetch(`${API_URL}/repair-requests/${requestId}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayOffersModal(data.repairRequest, data.offers);
        }
    } catch (error) {
        alert('Error loading offers: ' + error.message);
    }
}

function displayOffersModal(request, offers) {
    if (!offers || offers.length === 0) {
        alert('No offers yet for this request.');
        return;
    }
    
    const offersHtml = offers.map(offer => `
        <div class="offer-item">
            <div>
                <strong>${offer.handyman.name}</strong>
                <br>Rating: ${offer.handyman.rating || 'N/A'} | Completed Jobs: ${offer.handyman.completedJobs}
                <br>Price: $${offer.price} | Duration: ${offer.estimatedDuration}
                <br>${offer.message ? `Message: ${offer.message}` : ''}
                <br>Skills: ${offer.handyman.skills.join(', ')}
            </div>
            <button class="btn-accept btn-small" onclick="acceptOffer('${request._id}', '${offer._id}')">Accept</button>
        </div>
    `).join('');
    
    const modal = document.createElement('div');
    modal.id = 'offerModal';
    modal.style.display = 'flex';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close-modal" onclick="closeModal()">&times;</span>
            <h3>Offers for: ${request.title}</h3>
            <div class="offers-list">${offersHtml}</div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function closeModal() {
    const modal = document.getElementById('offerModal');
    if (modal) {
        modal.remove();
    }
}

async function acceptOffer(requestId, offerId) {
    try {
        const response = await fetch(`${API_URL}/repair-requests/${requestId}/accept-offer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ offerId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Offer accepted successfully!');
            closeModal();
            loadCustomerRequests();
        } else {
            alert(data.error || 'Failed to accept offer');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function completeRequest(requestId) {
    try {
        const response = await fetch(`${API_URL}/repair-requests/${requestId}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ status: 'completed' })
        });
        
        if (response.ok) {
            alert('Request marked as completed!');
            loadCustomerRequests();
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function loadAvailableJobs() {
    try {
        const response = await fetch(`${API_URL}/repair-requests`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayAvailableJobs(data.repairRequests);
        }
    } catch (error) {
        console.error('Error loading jobs:', error);
    }
}

function displayAvailableJobs(jobs) {
    const container = document.getElementById('availableJobs');
    
    if (!jobs || jobs.length === 0) {
        container.innerHTML = '<p>No jobs available nearby at the moment.</p>';
        return;
    }
    
    container.innerHTML = jobs.map(job => `
        <div class="job-card">
            <h4>${job.title}</h4>
            <p><strong>Category:</strong> ${job.category}</p>
            <p><strong>Description:</strong> ${job.description}</p>
            <p><strong>Urgency:</strong> <span class="badge ${job.urgency}">${job.urgency}</span></p>
            <p><strong>Location:</strong> ${job.location.address}</p>
            ${job.scheduledDate ? `<p><strong>Scheduled:</strong> ${new Date(job.scheduledDate).toLocaleString()}</p>` : ''}
            ${job.budget ? `<p><strong>Budget:</strong> $${job.budget.min || 0} - $${job.budget.max || 0}</p>` : ''}
            <p><strong>Customer:</strong> ${job.customer.name} (Rating: ${job.customer.rating || 'N/A'})</p>
            <button onclick="makeOffer('${job._id}')">Make an Offer</button>
        </div>
    `).join('');
}

function makeOffer(requestId) {
    const price = prompt('Enter your price ($):');
    if (!price) return;
    
    const duration = prompt('Estimated duration (e.g., "2 hours", "1 day"):');
    if (!duration) return;
    
    const message = prompt('Optional message to customer (leave empty to skip):');
    
    submitOffer(requestId, parseFloat(price), duration, message);
}

async function submitOffer(requestId, price, duration, message) {
    try {
        const response = await fetch(`${API_URL}/offers`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                repairRequestId: requestId,
                price,
                estimatedDuration: duration,
                message
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Offer submitted successfully!');
            loadMyOffers();
        } else {
            alert(data.error || 'Failed to submit offer');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function loadMyOffers() {
    try {
        const response = await fetch(`${API_URL}/offers/my-offers`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayMyOffers(data.offers);
        }
    } catch (error) {
        console.error('Error loading offers:', error);
    }
}

function displayMyOffers(offers) {
    const container = document.getElementById('myOffers');
    
    if (!offers || offers.length === 0) {
        container.innerHTML = '<p>You haven\'t made any offers yet.</p>';
        return;
    }
    
    container.innerHTML = offers.map(offer => `
        <div class="offer-card">
            <h4>${offer.repairRequest.title}</h4>
            <p><strong>Your Price:</strong> $${offer.price}</p>
            <p><strong>Estimated Duration:</strong> ${offer.estimatedDuration}</p>
            ${offer.message ? `<p><strong>Your Message:</strong> ${offer.message}</p>` : ''}
            <p><strong>Status:</strong> <span class="badge ${offer.status}">${offer.status}</span></p>
            <p><strong>Submitted:</strong> ${new Date(offer.createdAt).toLocaleString()}</p>
            <p><strong>Job Location:</strong> ${offer.repairRequest.location.address}</p>
            ${offer.status === 'accepted' ? '<p style="color: green; font-weight: bold;">Congratulations! Your offer was accepted. Contact the customer to schedule the job.</p>' : ''}
        </div>
    `).join('');
}
