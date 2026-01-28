const jwt = require('jsonwebtoken');

const authMiddleware = async (req, res, next) => {
  try {
    const token = req.header('Authorization')?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key');
    req.userId = decoded.userId;
    req.userType = decoded.userType;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
};

const requireHandyman = (req, res, next) => {
  if (req.userType !== 'handyman') {
    return res.status(403).json({ error: 'Handyman access required' });
  }
  next();
};

const requireCustomer = (req, res, next) => {
  if (req.userType !== 'customer') {
    return res.status(403).json({ error: 'Customer access required' });
  }
  next();
};

module.exports = { authMiddleware, requireHandyman, requireCustomer };
