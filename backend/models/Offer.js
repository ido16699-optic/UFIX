const mongoose = require('mongoose');

const offerSchema = new mongoose.Schema({
  repairRequest: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'RepairRequest',
    required: true
  },
  handyman: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  price: {
    type: Number,
    required: true
  },
  estimatedDuration: {
    type: String,
    required: true
  },
  message: {
    type: String
  },
  status: {
    type: String,
    enum: ['pending', 'accepted', 'rejected'],
    default: 'pending'
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Offer', offerSchema);
