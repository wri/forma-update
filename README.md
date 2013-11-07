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

1. API keys: we [look for](https://github.com/wri/forma-update/blob/master/formaupdate/runner.py#L23) `CARTODB_API_KEY` in your environment, so make sure it's available.
2. Install dependencies: `sudo pip install -r requirements.txt`.

### Updating the table driving the FORMA data on the website

From the CartoDB web interface:

1. Pull in the `gfw2_forma` schema: `SELECT * FROM gfw2_forma limit 1`.
2. Create a table from the query, calling it gfw2_forma_ew (or the like).
3. Delete the one record: `DELETE FROM gfw2_forma_ew`
4. Make the table public - DO NOT FORGET TO DO THIS!

Then, from your terminal:

1. If necessary, change the default table name in `runner.py` to match the new table you created.
2. Run `main()` in `runner.py`.
3. Swap out the existing `gfw2_forma table` for `gfw2_forma_ew`:

```sql
ALTER TABLE gfw2_forma RENAME TO gfw2_forma_bu;
ALTER TABLE gfw2_forma_ew1 RENAME TO gfw2_forma;
```

If something breaks and you need to switch things back, just run this:

```sql
ALTER TABLE gfw2_forma RENAME TO gfw2_forma_ew1;
ALTER TABLE gfw2_forma_bu RENAME TO gfw2_forma;
```

### Closing thoughts

A full update takes a bit less than half an hour. Old data may still
be cached until the website is redeployed. In the meantime, behavior
may be a bit strange, so be sure to coordinate with the folks at
Vizzuality about updates, and be ready to switch things back to the
old table if something has gone awry. We're messing with some rather
large tables here (on the order of a gig or two), so it can take a
while for changes to propagate to the cache, for the dashboard to
refresh, etc. Just give it some time and it'll work out fine.
