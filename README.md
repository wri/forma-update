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

This project does the SQL jiu jitsu needed to transform the CDM into a
data cube suitable for visualization. It is based on @andrewxhill's
SQL statement magic.

### Setup

1. API keys: we [look for](https://github.com/wri/forma-update/blob/a47d3220667f5a868c4a26e61b09cae15a2b1cc1/formaupdate/runner.py#L11) `CARTODB_API_KEY` in your environment, so make sure it's available.
2. Install dependencies: `sudo pip install -r requirements.txt`.

### Updating the table driving the FORMA data on the website

From the CartoDB web interface:

1. Pull in the `gfw2_forma` schema: `SELECT * FROM gfw2_forma limit 1`.
2. Create a table from the query, calling it `gfw2_forma_ew` (or the like).
3. Delete the one record: `DELETE FROM gfw2_forma_ew`
4. Make the table public - DO NOT FORGET TO DO THIS!
5. Upload the CDM file from S3. Rename it `cdm_latest_ew`
6. Drop some ecoregions from the table.

```sql
DELETE FROM cdm_latest WHERE ecoregion = '60122' OR ecoregion = '60147' OR ecoregion = '30109' OR ecoregion = '40134' OR ecoregion = '40150' OR ecoregion = '40131' OR ecoregion = '40136' OR ecoregion = '40126' OR ecoregion = '30130' OR ecoregion = '40141'
```

Then, get ready to run some Python code:

1. If necessary, change the default table name in `runner.py` to match the new `gfw_forma_ew` and `cdm_latest_ew` tables you've created.
2. Run `main()` in `runner.py`. This will do some sanity checking of the results as the process runs.
3. If you want to double-check the results before making the new table live, run [check_zooms()](https://github.com/wri/forma-update/blob/2fd664fcd7095850fa4a8e0de7507279a113dd9c/formaupdate/runner.py#L123-129)
4. Swap out the existing `gfw2_forma` table for `gfw2_forma_ew` using the web interface to rename the tables. DO NOT USE `ALTER TABLE` COMMANDS. If something breaks and you need to switch things back, just change the names again.

### Closing thoughts

A full update takes a bit less than half an hour. Old data may still
be cached until the website is redeployed. In the meantime, behavior
may be a bit strange, so be sure to coordinate with the folks at
Vizzuality about updates, and be ready to switch things back to the
old table if something has gone awry. We're messing with some rather
large tables here (on the order of a gig or two), so it can take a
while for changes to propagate to the cache, for the dashboard to
refresh, etc. Just give it some time and it'll work out fine.
