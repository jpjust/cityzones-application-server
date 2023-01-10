# Data reading for sending coordinates to the browser

Read data line by line instead of reading it all at once. Actually this is being done already, but think of streaming it to the browser instead of sending at once. Check the size of an int in Python to see if storing a list of all coordinates uses too much memory or not.

Another point is to not send all the points, but an interpolarized version with less points (set a maximum number of points).

# Checkbox to not re-center the map

Add a checkbox to disable re-centering the map when loading another result.

# Add a feedback to "Show map" button

Maybe a "Loading..." string just to let the user knows that the map is loading.

# Add metadata to the tasks

Maybe a description and who requested it, then show it in the results list so it would be easier to know about a task before loading its results. Also show the CSV data size.

# Limit grid size

Maybe it will be a good idea to limit grid size and avoid using too much memory at the worker site.

# Final expiration

If a task takes too long to get done (a couple of days, for example), flag it as problematic and stop serving it.

# Other functionalities

- More PoIs categories
- EDUs settings
- Paginate results list
