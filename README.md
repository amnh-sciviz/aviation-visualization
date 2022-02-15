# Aviation Visualization

Visualization of global flights for pandemic video

## Data source

[Open Flights](https://openflights.org/data.html)

## Requirements

1. Python 3.6+
2. [ffmpeg](https://www.ffmpeg.org/) (for generating video)
3. Install Python modules:

    ```
    pip install -r requirements.txt
    ```

## Running the script

To just export the frames (with no map background), overwriting any existing frames:

```
python run.py -overwrite
```

Export frames and video with a map background:

```
python run.py -map -overwrite
```

There are a number of other options available:

```
python run.py -h
```
