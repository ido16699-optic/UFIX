const express = require('express');
const RepairRequest = require('../models/RepairRequest');
const Offer = require('../models/Offer');
const User = require('../models/User');
const { authMiddleware, requireCustomer } = require('../middleware/auth');

const router = express.Router();

// Create a repair request
router.post('/', authMiddleware, requireCustomer, async (req, res) => {
  try {
    const { title, description, category, location, urgency, scheduledDate, budget, images } = req.body;

    const repairRequest = new RepairRequest({
      customer: req.userId,
      title,
      description,
      category,
      location,
      urgency,
      scheduledDate: urgency === 'scheduled' ? scheduledDate : undefined,
      budget,
      images
    });

    await repairRequest.save();

    res.status(201).json({
      message: 'Repair request created successfully',
      repairRequest
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get all repair requests (for customers - their own, for handymen - nearby)
router.get('/', authMiddleware, async (req, res) => {
  try {
    let query = {};

    if (req.userType === 'customer') {
      // Customers see only their own requests
      query.customer = req.userId;
    } else if (req.userType === 'handyman') {
      // Handymen see open requests
      query.status = 'open';
      
      // Get handyman location for proximity search
      const handyman = await User.findById(req.userId);
      if (handyman && handyman.location && handyman.location.coordinates) {
        const maxDistance = 50000; // 50km in meters
        query.location = {
          $near: {
            $geometry: {
              type: 'Point',
              coordinates: handyman.location.coordinates
            },
            $maxDistance: maxDistance
          }
        };
      }
    }

    const requests = await RepairRequest.find(query)
      .populate('customer', 'name phone rating')
      .sort({ createdAt: -1 });

    res.json({ repairRequests: requests });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get a specific repair request with offers
router.get('/:id', authMiddleware, async (req, res) => {
  try {
    const repairRequest = await RepairRequest.findById(req.params.id)
      .populate('customer', 'name phone rating');

    if (!repairRequest) {
      return res.status(404).json({ error: 'Repair request not found' });
    }

    // Get offers for this request
    const offers = await Offer.find({ repairRequest: req.params.id })
      .populate('handyman', 'name rating completedJobs skills');

    res.json({ repairRequest, offers });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Accept an offer
router.post('/:id/accept-offer', authMiddleware, requireCustomer, async (req, res) => {
  try {
    const { offerId } = req.body;

    const repairRequest = await RepairRequest.findById(req.params.id);
    if (!repairRequest) {
      return res.status(404).json({ error: 'Repair request not found' });
    }

    if (repairRequest.customer.toString() !== req.userId) {
      return res.status(403).json({ error: 'Not authorized' });
    }

    const offer = await Offer.findById(offerId);
    if (!offer) {
      return res.status(404).json({ error: 'Offer not found' });
    }

    // Update offer status
    offer.status = 'accepted';
    await offer.save();

    // Update repair request
    repairRequest.selectedOffer = offerId;
    repairRequest.status = 'in_progress';
    await repairRequest.save();

    // Reject other offers
    await Offer.updateMany(
      { repairRequest: req.params.id, _id: { $ne: offerId } },
      { status: 'rejected' }
    );

    res.json({
      message: 'Offer accepted successfully',
      repairRequest,
      offer
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Update repair request status
router.patch('/:id/status', authMiddleware, async (req, res) => {
  try {
    const { status } = req.body;

    const repairRequest = await RepairRequest.findById(req.params.id);
    if (!repairRequest) {
      return res.status(404).json({ error: 'Repair request not found' });
    }

    repairRequest.status = status;
    await repairRequest.save();

    // If completed, update handyman's stats
    if (status === 'completed' && repairRequest.selectedOffer) {
      const offer = await Offer.findById(repairRequest.selectedOffer);
      if (offer) {
        await User.findByIdAndUpdate(offer.handyman, {
          $inc: { completedJobs: 1 }
        });
      }
    }

    res.json({
      message: 'Status updated successfully',
      repairRequest
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
