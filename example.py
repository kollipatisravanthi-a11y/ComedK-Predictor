"""
Example usage of the COMEDK Rank Predictor.
This script demonstrates how to use the predictor programmatically.
"""

from predictor import RankPredictor
import sys

def main():
    """Main function to demonstrate predictor usage."""
    print("=" * 60)
    print("COMEDK Rank Predictor - Example Usage")
    print("=" * 60)
    print()
    
    try:
        # Initialize the predictor
        print("Loading predictor model...")
        predictor = RankPredictor()
        print("✓ Model loaded successfully!\n")
        
        # Example predictions with different score levels
        examples = [
            {
                'name': 'Excellent Performance',
                'physics': 55,
                'chemistry': 58,
                'math': 60
            },
            {
                'name': 'Very Good Performance',
                'physics': 45,
                'chemistry': 48,
                'math': 50
            },
            {
                'name': 'Good Performance',
                'physics': 35,
                'chemistry': 38,
                'math': 40
            },
            {
                'name': 'Average Performance',
                'physics': 25,
                'chemistry': 28,
                'math': 30
            }
        ]
        
        # Run predictions
        for example in examples:
            print(f"{'=' * 60}")
            print(f"Example: {example['name']}")
            print(f"{'=' * 60}")
            
            result = predictor.get_rank_insights(
                physics_score=example['physics'],
                chemistry_score=example['chemistry'],
                math_score=example['math']
            )
            
            # Display results
            print(f"\n📊 Input Scores:")
            print(f"   Physics:     {result['subject_scores']['physics']:.2f}/60")
            print(f"   Chemistry:   {result['subject_scores']['chemistry']:.2f}/60")
            print(f"   Mathematics: {result['subject_scores']['mathematics']:.2f}/60")
            print(f"   Total:       {result['total_score']:.2f}/180")
            
            print(f"\n🎯 Prediction Results:")
            print(f"   Predicted Rank: {result['predicted_rank']:,}")
            print(f"   Rank Range:     {result['rank_range']['lower']:,} - {result['rank_range']['upper']:,}")
            print(f"   Category:       {result['performance_category']}")
            
            print(f"\n💡 Insight:")
            print(f"   {result['message']}")
            print()
        
        print("=" * 60)
        print("Want to predict your own rank?")
        print("Run the web application: python app.py")
        print("Then visit: http://localhost:5000")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        print("\nPlease run the following commands first:")
        print("  1. python data_generator.py")
        print("  2. python train_model.py")
        sys.exit(1)
    except Exception as e:
        print(f"✗ An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
