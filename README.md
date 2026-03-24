# Black Bear Foodshare

Black Bear Foodshare is an iOS application designed to connect UMaine students with leftover food from campus events and dining facilities, reducing food waste and addressing food insecurity.

## Project Structure

- backend: Quart (Python) asynchronous API and SQLite database.
- frontend: SwiftUI iOS application using MVVM architecture.
- documents: Project requirements, design specifications, and reports.

## Backend Setup

The backend requires Python 3.12 or later.

1. Navigate to the backend directory:
   cd backend

2. Create and activate a virtual environment:
   python3 -m venv .venv
   source .venv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

4. Run the application:
   quart --app src.app run

The API will be available at http://localhost:5000.

## Backend Testing and Linting

1. Run all tests:
   pytest

2. Run linter:
   ruff check

3. Run formatter:
   ruff format

## Frontend Setup

The frontend requires a Mac with Xcode 16.0 or later installed.

1. Open the workspace file at the root of the repository:
   open BBFS.xcworkspace

2. Select the BlackBearFoodShare scheme and an iOS Simulator (e.g., iPhone 16).

3. Press Command+R to build and run the application.

## Frontend Testing

1. Run unit and UI tests:
   xcodebuild -workspace BBFS.xcworkspace -scheme BlackBearFoodShare -sdk iphonesimulator test -destination 'platform=iOS Simulator,name=iPhone 16'

Alternatively, press Command+U within Xcode to run tests.
