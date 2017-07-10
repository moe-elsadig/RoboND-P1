## Project: Search and Sample Return
### Writeup Template: You can use this file as a template for your writeup if you want to submit it as a markdown file, but feel free to use some other method and submit a pdf if you prefer.

---


**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook).
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands.
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  

[//]: # (Image References)

[image1]: ./misc/rover_image.jpg
[image2]: ./calibration_images/example_grid1.jpg
[image3]: ./calibration_images/example_rock1.jpg
[image4]: ./output/coor_image.jpg
[image5]: ./output/coor_threshed.jpg
[image6]: ./output/coor_transformed.jpg
[image7]: ./output/coor_warp.jpg
[image8]: ./output/process_image_output.jpg
[image9]: ./output/test_mapping.mp4
[image10]: ./output/warped_example.jpg
[image11]: ./output/warped_nav_terrain.jpg
[image12]: ./output/warped_obs_terrain.jpg
[image13]: ./output/warped_rock.jpg
[image14]: ./output/warped_rocks.jpg
[image15]: ./output/test_mapping2.mp4

## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

![alt text][image1]

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

You're reading it!

and here are the calibration images:

![alt text][image2]
![alt text][image3]

## Perspective Transform

### Task:

Define the perspective transform function from the lesson and test it on an image.
> (perception.py: 106-111)

### Solution:

By selecting source coordinates and destination coordinates, we are essentially outlining a sample transformation that the openCV function uses to warp the rest of the image in a respectively equal fashion.

By performing a perspective transform to a mimic a top-down camera view (with a reduced FOV) to study the surrounding of our rover.

Here I have used to experimentally obtained coordinates that visually matched the sample transformation image the most, making sure that the grid lines remained parallel as far as can be seen with respect to the increasing distortion the further you are from the camera.
> (perception.py: 120-130)

As per the note stating the camera's position on the rover itself, the transformed image is slightly pulled further towards the bottom, this gives us the effect of mapping what the car sees immediately after the rover only.

![alt text][image10]


## Color Thresholding

### Task:

Define the color thresholding function from the lesson and apply it to the warped image.
> (perception.py: 6-51)

### Solution:

![alt text][image13]

> (perception.py: 132-133)

#### Navigable terrain:
Navigable terrain is the first step to solving this task, and to obtain the best results by experimentation, we make use of IPyWidgets, specifically, Interact.
With interact we can specify three sliders (ranges, 0-255) and watch as we drag how changing each value affects our desired output.

Eventually I landed on the values (200,150,150) for r, g, and b respectively. I feel red has the strongest effect when trying to distinguish dark and light areas in an image.
> (perception.py: 39)

![alt text][image11]

#### Obstacles:
Needless to say, obstacles are anywhere we can't go, so flipping our output from navigable terrain, or reversing our threshold might be all that's needed. Not entirely.

We can start by reversing the navigable terrain output but we'll end up with a false obstacle detection for the the entire area outside our field of view.

To counter this effect we can theoretically map the entire field of view as an obstacle with the help of a mask, and subtract our inverted navigable terrain output. With this we end up with an image of obstacles only within our current FOV.
> (perception.py: 40,45-48)

![alt text][image12]

#### Rocks:
The specimens we wish to find are of a specific colour, in this case yellow. In the RGB colour space, R and G are the two channels mainly responsible with reproducing the colour yellow. Again by modifying our threshold and output to use Interact's sliders, we eventually end up with the values 75, 75 and 50 for RGB respectively with the relations (>, >, <).
> (perception.py: 41)

![alt text][image14]


## Coordinate Transformations

### Task:

Define the functions used to do coordinate transforms and apply them to an image.
> (perception.py: 53-103)

### Solution:

![alt text][image4]

**rover_coords:** This function converts from image coordinates to rover coordinates. The image after being warped starts it's (x,y) axes from the corner of the image. Rover centric coordinates means that the rover's position is at (0,0), positive x-axis is in front of the rover and positive y-axis is to the left of the rover.

![alt text][image7]
![alt text][image5]

**to_polar_coords:** This function just convert the rover centric Cartesian coordinates (x_rover, y_rover) to polar coordinates (dist_rover, angles_rover) still in rover centric coordinates. This can assist in calculating steering angles.

**pix_to_world:** This function combines the other two left-over functions **rotate_pix and translate_pix** to give us map coordinates. The reason we need map coordinates other than a lovely mini-map while the rover is moving, is that it helps to create a history of the terrain that's already been traversed and mark down landmarks and points of interest for later analysis (or rock retrieval in this case). To achieve this effect, our rover's current position and all other telemetry calculated up to this point is used to rotate and translate the pixels in a uniform and scaled manor to our world-map.

**Note:** A simple method of directing the rover through clear terrain is to average the angles obtain in the polar coordinate transformation and using it's angle away from origin to direct the rover's steering. This is a simplistic method full of corner-cases and might not be suitable for real-world applications.
> (perception.py: 148-166)

![alt text][image6]

## Write a function to process stored images

### Task:

Modify the `process_image()` function below by adding in the perception step processes (functions defined above) to perform image analysis and mapping.  The following cell is all set up to use this `process_image()` function in conjunction with the `moviepy` video processing package to create a video from the images you saved taking data in the simulator.  

In short, you will be passing individual images into `process_image()` and building up an image called `output_image` that will be stored as one frame of video.  You can make a mosaic of the various steps of your analysis process and add text as you like (example provided below).  

To start with, you can simply run the next three cells to see what happens, but then go ahead and modify them such that the output video demonstrates your mapping process.  Feel free to get creative!

### Solution:

just like with the functions above, now we need to fill out this function to automate the process into a pipeline with input images and output images.

**Step 1:**

Define the source and destination points for warping the image and mimic a top-down view. Here we used the same experimental values we concluded with earlier.

We then apply the perspective transform and receive the warped image.

**Step 2:**

Send the warped image to apply all the thresholds we defined in the color_thresh function above and receive three images for the navigable terrain, obstacles in view, and detected rocks respectively.

**Step 3:**

Convert the thresholded images into rover centric coordinates to be used for two functions. The first is to convert these Cartesian coordinates to polar distances and angles. The current method uses the angles to determine clear terrain and with it the steering angle. The second is to map the rovers position and what it sees to the world-map by scaling, translating and rotating the available telemetry.

The map information is passed in to different channels (obstacles = red, navigable = blue, yellow = green) for clear distinction and easy to read visualization.

> (perception.py: 168-181)

[![IMAGE ALT TEXT HERE](http://img.youtube.com/vi/WJ2f8S_dswg/0.jpg)](https://youtu.be/WJ2f8S_dswg)

**Step 4: note specific**
Initialize an empty array combining the dimensions of the image and map. Combine in this image the camera view, warped view, and live world-map.

![alt text][image8]
