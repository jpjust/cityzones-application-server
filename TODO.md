# Data reading for sending coordinates to the browser

Read data line by line instead of reading it all at once. Actually this is being done already, but think of streaming it to the browser instead of sending at once. Check the size of an int in Python to see if storing a list of all coordinates uses too much memory or not.

Another point is to not send all the points, but an interpolarized version with less points (set a maximum number of points).

Or limit the output. If the result has more than XXX coordinates, do not allow to send it.

Or just warn the user that the output may be too big and slow down its browser. If the user accepts, stream the coordinates instead of sending a JSON object at once.

# Limit grid size

Maybe it will be a good idea to limit grid size and avoid using too much memory at the worker site. One idea is to calculate the area of the AoI in server side and divide by zl to get the number of zones. It can be a zones limit to avoid huge tasks.

# Recreate a request

Add a button to the results list so that an user can open the map view with that settings and repeat the request (or change some settings for a new request).

# Other functionalities

- More PoIs categories
