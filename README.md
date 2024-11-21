# Segments Effort Scheduled Job
GitHub Action daily scheduled job to fetch and save segments effort count data from strava api

## Setup

To set up the project, follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/segments-effort-scheduled-job.git
    cd segments-effort-scheduled-job
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file based on the `.env.example` file and fill in the required environment variables:
    ```sh
    cp .env.example .env
    ```

## Adding Segments for a Specific Trail Area

To add segments for a specific trail area, follow these steps:

1. Open the `segment_ids.py` file located in the `segments_data` directory.

2. Locate the dictionary corresponding to the trail area you want to add segments to. For example, if you want to add segments to the "alghero" trail area, find the "alghero" dictionary.

3. Add a new entry to the dictionary with the Strava segment ID as the key and a description of the segment as the value. The description is not used by the code but can be helpful for reference.

Example:
```python
segment_ids = {
    "alghero": {
        "12345678": "New Segment Description",
        ...
    },
    ...
}
```

4. Save the segment_ids.py file.

When the script runs, it will automatically add the new segment to the database under the specified trail area.

**Note: Ensure that the segment ID is a valid Strava segment ID.**