import numpy as np
import cv2

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
# @interact(img=fixed(warped), rgb_thresh=fixed((-1, -1, -1)), r=(0,255,1), g=(0,255,1), b=(0,255,1))
def color_thresh(img, rgb_thresh=(-1, -1, -1), r=200 , g=150 , b=150):
    
    # check which method was used to pass the threshold values with
    if(rgb_thresh[0] > -1):
        r = rgb_thresh[0]
        g = rgb_thresh[1]
        b = rgb_thresh[2]
        
    # Create an array of zeros same xy size as img, but single channel
    navigable = np.zeros_like(img[:,:,0])
    obstacle = np.zeros_like(img[:,:,0])
    rock = np.zeros_like(img[:,:,0])
    
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > r) \
                & (img[:,:,1] > g) \
                & (img[:,:,2] > b)
            
    below_thresh = (img[:,:,0] < r) \
                & (img[:,:,1] < g) \
                & (img[:,:,2] < b)
            
    rock_thresh = (img[:,:,0] > 75) \
                & (img[:,:,1] > 75) \
                & (img[:,:,2] < 50)

    # Index the array of zeros with the boolean array and set to 1
    navigable[above_thresh] = 1
    obstacle[below_thresh] = 1
    rock[rock_thresh] = 1
    
    # plt.imshow(rock, cmap='gray') # Uncomment when using interact in the above cell to see the
    # results
    # plt.clf()

    # Return the binary image
    return navigable, obstacle, rock

# Define a function to convert from image coords to rover coords
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    img = Rover.img

    # 1) Define source and destination points for perspective transform
    source = np.float32([[120, 95], 
                 [10, img.shape[0]-20], 
                 [img.shape[1]-10, img.shape[0]-20], 
                 [img.shape[1]-120, 95]])
    destination = np.float32([[img.shape[1]/2-5, img.shape[0]-10], 
                 [img.shape[1]/2-5, img.shape[0]+5], 
                 [img.shape[1]/2+5, img.shape[0]+5], 
                 [img.shape[1]/2+5, img.shape[0]-10]])       

    # 2) Apply perspective transform
    warped = perspect_transform(img, source, destination)

    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    nav_terrain, obstacles, rocks = color_thresh(img)

    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
        # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image

    Rover.vision_image[:,:,0] = obstacles
    Rover.vision_image[:,:,1] = rocks
    Rover.vision_image[:,:,2] = nav_terrain


    # 5) Convert map image pixel values to rover-centric coords
    nav_xpix, nav_ypix = rover_coords(nav_terrain)
    obs_xpix, obs_ypix = rover_coords(obstacles)
    rock_xpix, rock_ypix = rover_coords(rocks)

    # 6) Convert rover-centric pixel values to world coordinates
    nav_dists, nav_angles = to_polar_coords(nav_xpix, nav_ypix)
    obs_dists, obs_angles = to_polar_coords(obs_xpix, obs_ypix)
    rock_dists, rock_angles = to_polar_coords(rock_xpix, rock_ypix)

    # 7) Update Rover worldmap (to be displayed on right side of screen)
        # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1
    xpos = Rover.xpos[Rover.count]
    ypos = Rover.ypos[Rover.count]
    yaw = Rover.yaw[Rover.count]
    world_size = 200
    scale = 10

    nav_xpix_world, nav_ypix_world = pix_to_world(nav_xpix, nav_ypix, xpos, ypos, yaw, world_size, scale)
    obs_xpix_world, obs_ypix_world = pix_to_world(obs_xpix, obs_ypix, xpos, ypos, yaw, world_size, scale)
    rock_xpix_world, rock_ypix_world = pix_to_world(obs_xpix, obs_ypix, xpos, ypos, yaw, world_size, scale)
        
    Rover.worldmap[nav_ypix_world, nav_xpix_world, 2] += 1
    Rover.worldmap[obs_ypix_world, obs_xpix_world, 0] += 1
    Rover.worldmap[rock_ypix_world, rock_xpix_world, 1] += 1

    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
        # Rover.nav_dists = rover_centric_pixel_distances
        # Rover.nav_angles = rover_centric_angles
    nav_dists, nav_angles = to_polar_coords(nav_xpix, nav_ypix)
    obs_dists, obs_angles = to_polar_coords(obs_xpix, obs_ypix)
    rock_dists, rock_angles = to_polar_coords(rock_xpix, rock_ypix)
    
    Rover.nav_dists = nav_dists
    Rover.nav_angles = nav_angles

    Rover.count += 1
    
    return Rover
