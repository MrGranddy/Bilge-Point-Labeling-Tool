# Bilge Point Labeling Tool

These set of scripts helps you label points on an image, it is easy and fast to use.

### Prerequisites

Here is a quick list of the things you'll have to run this program.

```
Python 3.6 or higher
```
```
PyGame
```
```
Pillow
```
```
Numpy
```

## Running the test

"tool.py" main script to label your images.
"edit.py" script to edit a previous spesific image or label a new one.
"test.py" see through your previous labels.

## How to run the program?

First you have to create two directories in the directory which the main program sits.
One is "img" the other is "data". You do not need to put anything in the data folder but
you should put the images you want to annotate into the img folder.
After the setup is done you can run the program with
```
>>> python3 tool.py
```

To edit a previous one or label a specific one
```
>>> python3 edit.py {image_name} # image name can have the img/ directory prefix or not, it is handled.
```

## How to use the program?

* Creating a Point
```
Left click somewhere on the image and label that point.
```

* Deleting a point
```
Right click in the radius of a point, it is deleted!
```

* Zooming
```
Use your arrow keys, up is zoom down is zoom out.
```

* Working on the Next Picture
```
Press ENTER or RETURN key to move to the next image. Current labels are saved and new image from the img/ folder is loaded.
```

