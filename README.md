# McDo Survey Bot

A Python bot with a web control panel for automating McDonald's customer satisfaction surveys.

## Features

- Automated completion of McDonald's customer satisfaction surveys
- Web-based control panel accessible via localhost
- Single survey mode with configurable options
- Bulk survey mode for running multiple surveys
- Detailed logging of all survey submissions
- Dashboard with statistics and activity monitoring

## Requirements

- Python 3.8+
- Chrome browser installed
- Required Python packages (see requirements.txt)

## Installation

1. Clone this repository:
```
git clone <repository-url>
cd <repository-directory>
```

2. Create a virtual environment and activate it:
```
python -m venv venv
# On Windows
venv\Scripts\activate
# On MacOS/Linux
source venv/bin/activate
```

3. Install the required packages:
```
pip install -r requirements.txt
```

## Usage

1. Start the web control panel:
```
python run.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Use the control panel to:
   - Run a single survey with custom parameters
   - Run multiple surveys in bulk
   - View survey logs and statistics

## Bot Operation

### Single Survey Mode

This mode allows you to specify:
- Age group selection
- Receipt date
- Receipt time
- Restaurant number
- Headless mode toggle (hide browser window)

If fields are left empty, random values will be generated.

### Bulk Mode

This mode allows you to run multiple surveys automatically with random values. You can specify:
- Number of surveys to run (max 50)
- Headless mode toggle

## Development

The application follows a Model-View-Controller (MVC) architecture:

- `/app/models/` - Database models
- `/app/controllers/` - Business logic and bot implementation
- `/app/routes/` - Flask routes and request handling
- `/app/templates/` - HTML templates
- `/app/static/` - Static assets (CSS, JS)

## Security Note

This tool is for educational purposes only. Please use responsibly and in accordance with the terms of service of any websites you interact with. The developers are not responsible for any misuse of this software. 