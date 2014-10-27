forma-update
============

This is a set of scripts to update the FORMA data on the GFW site.

### The big idea

Vizzuality figured out how to use data cubes to visualize detailed
spatio-temporal data. This project takes FORMA data stored in a table
using our Common Data Model (CDM - see below), and massages it into
the format needed for rapid, interactive visualization on the GFW website.

The CDM is a simple format that records points in map-tile coordinates
and stores an occurrence date index. The basic schema is `x,y,z,p`,
where `x`, `y` and `z` are map tile coordinates, and `p` is the period
index. For FORMA data, this is a monthly period index where 0 is
January 2000. In practice, we usually include a few more fields like
latitude, longitude, and iso code, just for convenience and
quick/dirty data exploration and visualization.

### 
