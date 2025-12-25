document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictionForm');
    const resultsDiv = document.getElementById('results');
    const errorDiv = document.getElementById('error');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Hide previous results/errors
        resultsDiv.style.display = 'none';
        errorDiv.style.display = 'none';

        // Get form values
        const physicsScore = parseFloat(document.getElementById('physics').value);
        const chemistryScore = parseFloat(document.getElementById('chemistry').value);
        const mathScore = parseFloat(document.getElementById('math').value);

        // Validate inputs
        if (isNaN(physicsScore) || isNaN(chemistryScore) || isNaN(mathScore)) {
            showError('Please enter valid scores for all subjects.');
            return;
        }

        if (physicsScore < 0 || physicsScore > 60 || 
            chemistryScore < 0 || chemistryScore > 60 || 
            mathScore < 0 || mathScore > 60) {
            showError('All scores must be between 0 and 60.');
            return;
        }

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Predicting...';
        submitBtn.disabled = true;

        try {
            // Make prediction request
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    physics_score: physicsScore,
                    chemistry_score: chemistryScore,
                    math_score: mathScore
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Prediction failed');
            }

            // Display results
            displayResults(data);

        } catch (error) {
            showError(error.message);
        } finally {
            // Reset button
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    });

    function displayResults(data) {
        // Update total score
        document.getElementById('totalScore').textContent = data.total_score.toFixed(2);

        // Update predicted rank
        document.getElementById('predictedRank').textContent = 
            data.predicted_rank.toLocaleString();

        // Update rank range
        document.getElementById('rankRange').textContent = 
            `${data.rank_range.lower.toLocaleString()} - ${data.rank_range.upper.toLocaleString()}`;

        // Update performance category
        document.getElementById('category').textContent = data.performance_category;
        document.getElementById('message').textContent = data.message;

        // Update subject scores
        document.getElementById('physicsDisplay').textContent = 
            `${data.subject_scores.physics.toFixed(2)} / 60`;
        document.getElementById('chemistryDisplay').textContent = 
            `${data.subject_scores.chemistry.toFixed(2)} / 60`;
        document.getElementById('mathDisplay').textContent = 
            `${data.subject_scores.mathematics.toFixed(2)} / 60`;

        // Update performance badge color based on category
        const badge = document.getElementById('performanceBadge');
        badge.style.background = getCategoryGradient(data.performance_category);

        // Show results
        resultsDiv.style.display = 'block';
        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function getCategoryGradient(category) {
        const gradients = {
            'Excellent': 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
            'Very Good': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            'Good': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            'Average': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            'Needs Improvement': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
        };
        return gradients[category] || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    }

    function showError(message) {
        document.getElementById('errorMessage').textContent = message;
        errorDiv.style.display = 'block';
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // Add input validation
    const inputs = form.querySelectorAll('input[type="number"]');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (value < 0) this.value = 0;
            if (value > 60) this.value = 60;
        });
    });
});
