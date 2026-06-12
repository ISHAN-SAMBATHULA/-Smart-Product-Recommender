"""Quick setup script — install dependencies and generate dataset."""
import subprocess
import sys
import os

def main():
    print("=" * 60)
    print("  Amazon Product Recommendation System — Setup")
    print("=" * 60)
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                          "streamlit", "pandas", "numpy", "scikit-learn", "plotly", "scipy"])
    
    # Generate dataset
    print("\n🔧 Generating synthetic dataset...")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    from data.generate_data import build_database
    build_database()
    
    print("\n✅ Setup complete! Run the app with:")
    print("   streamlit run app.py")

if __name__ == "__main__":
    main()
