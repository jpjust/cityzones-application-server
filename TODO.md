# Data reading for sending coordinates to the browser

Read data line by line instead of reading it all at once. Actually this is being done already, but think of streaming it to the browser instead of sending at once. Check the size of an int in Python to see if storing a list of all coordinates uses too much memory or not.

Another point is to not send all the points, but an interpolarized version with less points (set a maximum number of points).

# Download config and GeoJSON

Add a button to download config and GeoJSON of a task.

# Limit grid size

Maybe it will be a good idea to limit grid size and avoid using too much memory at the worker site.

# Final expiration

If a task takes too long to get done (a couple of days, for example), flag it as problematic and stop serving it.

# Recreate a request

Add a button to the results list so that an user can open the map view with that settings and repeat the request (or change some settings for a new request).

# Other functionalities

- More PoIs categories
