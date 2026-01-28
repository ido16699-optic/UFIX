const express = require('express');
const Offer = require('../models/Offer');
const RepairRequest = require('../models/RepairRequest');
const { authMiddleware, requireHandyman } = require('../middleware/auth');

const router = express.Router();

// Create an offer
router.post('/', authMiddleware, requireHandyman, async (req, res) => {
  try {
    const { repairRequestId, price, estimatedDuration, message } = req.body;

    // Check if repair request exists and is open
    const repairRequest = await RepairRequest.findById(repairRequestId);
    if (!repairRequest) {
      return res.status(404).json({ error: 'Repair request not found' });
    }

    if (repairRequest.status !== 'open') {
      return res.status(400).json({ error: 'Repair request is not open for offers' });
    }

    // Check if handyman already made an offer
    const existingOffer = await Offer.findOne({
      repairRequest: repairRequestId,
      handyman: req.userId
    });

    if (existingOffer) {
      return res.status(400).json({ error: 'You have already made an offer for this request' });
    }

    const offer = new Offer({
      repairRequest: repairRequestId,
      handyman: req.userId,
      price,
      estimatedDuration,
      message
    });

    await offer.save();

    res.status(201).json({
      message: 'Offer submitted successfully',
      offer
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get handyman's offers
router.get('/my-offers', authMiddleware, requireHandyman, async (req, res) => {
  try {
    const offers = await Offer.find({ handyman: req.userId })
      .populate('repairRequest')
      .sort({ createdAt: -1 });

    res.json({ offers });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Update an offer
router.patch('/:id', authMiddleware, requireHandyman, async (req, res) => {
  try {
    const { price, estimatedDuration, message } = req.body;

    const offer = await Offer.findOne({ _id: req.params.id, handyman: req.userId });
    if (!offer) {
      return res.status(404).json({ error: 'Offer not found' });
    }

    if (offer.status !== 'pending') {
      return res.status(400).json({ error: 'Cannot update accepted or rejected offers' });
    }

    if (price) offer.price = price;
    if (estimatedDuration) offer.estimatedDuration = estimatedDuration;
    if (message) offer.message = message;

    await offer.save();

    res.json({
      message: 'Offer updated successfully',
      offer
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
