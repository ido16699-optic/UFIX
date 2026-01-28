const mongoose = require('mongoose');

const repairRequestSchema = new mongoose.Schema({
  customer: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  category: {
    type: String,
    required: true,
    enum: ['plumbing', 'electrical', 'carpentry', 'painting', 'general', 'other']
  },
  location: {
    type: {
      type: String,
      enum: ['Point'],
      default: 'Point'
    },
    coordinates: {
      type: [Number],
      required: true
    },
    address: {
      type: String,
      required: true
    }
  },
  urgency: {
    type: String,
    enum: ['asap', 'scheduled'],
    default: 'asap'
  },
  scheduledDate: {
    type: Date
  },
  budget: {
    min: Number,
    max: Number
  },
  images: [{
    type: String
  }],
  status: {
    type: String,
    enum: ['open', 'in_progress', 'completed', 'cancelled'],
    default: 'open'
  },
  selectedOffer: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Offer'
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

// Index for geospatial queries
repairRequestSchema.index({ location: '2dsphere' });

repairRequestSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

module.exports = mongoose.model('RepairRequest', repairRequestSchema);
