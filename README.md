# Photoscan

Photoscan is an application that calculates angle and position differences between two photos, especially photos made in different centuries.

Goal of this application was to simplify photo collection using volunteers' mobile phones to obtain exact spot and location of historical photo.

Vision was to use this project to:
- preserve how cities looked in the past
- create VR tours into different centuries
- see how cities change in time

This project was made as part of CS Bachelor's diploma.

CAUTION: this project is not maintained and may contain dependencies with vulnerabilities.

Historical photo          |  Position and angle estimation result
:-------------------------:|:-------------------------:
![Lviv Opera Theatre Historical Photo](examples/image-50.jpeg "Lviv Opera Theatre Historical Photo")  |  ![Lviv Opera Theatre Photo Parameters](examples/image-52.jpeg "Lviv Opera Theatre Photo Parameters")


# Application architecture

Application consists of two parts:

1. Mobile application, which have the following functions:
- takes photo and sends it to server
- obtains GPS coordinates, device compass heading and sends it to server

Mobile application            |  Result screen
:-------------------------:|:-------------------------:
![Application main screen](examples/image-42.png "Application main screen")  |  ![Application result screen](examples/image-46.png "Application result screen")

Tested only on Android!

2. Simple Python Tornado server, which calculates properties of photograph.
Angle and position is calculated using OpenCV library and [Speeded up robust features (SURF)](https://en.wikipedia.org/wiki/Speeded_up_robust_features) algorithm

# Attributions

Icons made by [monkik](https://www.flaticon.com/authors/monkik) from [www.flaticon.com](https://www.flaticon.com/") is licensed by  [Creative Commons BY 3.0](http://creativecommons.org/licenses/by/3.0)
