################################################
# Script for generating ontology documentation #
################################################
# Requirements:
# - Java 8 or higher
# - Python 3

# Create temp/ directory
mkdir -p temp/

# Set up the virtual environment required to run convert.py
if ! [[ -d "./venv" ]]
then
    python3 -m venv venv
    source venv/bin/activate
    pip3 install pylode
    pip3 install pyyaml
    pip3 install beautifulsoup4
else
    source venv/bin/activate
fi

# Run script
python3 convert.py