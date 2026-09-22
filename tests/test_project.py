from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def test_required_directories():
    for path in [ROOT/"data/raw",ROOT/"data/cleaned",ROOT/"data/processed",ROOT/"hadoop",ROOT/"spark",ROOT/"src",ROOT/"dashboard"]:
        assert path.exists(), f"Missing {path}"

def test_required_scripts():
    for path in [ROOT/"src/data_cleaning/validate_raw.py",ROOT/"src/data_cleaning/clean_data.py",ROOT/"spark/ipl_pipeline.py"]:
        assert path.exists(), f"Missing {path}"
