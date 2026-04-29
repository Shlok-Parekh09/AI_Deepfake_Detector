const express = require('express');
const router = express.Router();
const multer = require('multer');
const { analyzeMedia } = require('../controllers/analyzeController');

// Configure multer for file uploads (storing in memory for now)
const upload = multer({ storage: multer.memoryStorage() });

// POST endpoint for media analysis
// The 'file' field should match the form-data key from the frontend
router.post('/', upload.single('file'), analyzeMedia);

module.exports = router;
