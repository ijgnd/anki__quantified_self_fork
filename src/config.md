This is a port to Anki 2.1 of the add-on "Quantified Self add-on - export your review log - v0.2",
https://ankiweb.net/shared/info/1591779596

Extract review data in a way that lets you see how effective the memrization was on each day
useful for quantified self analysis, and answering questions like: 
"did I learn better on days I took caffeine?"

- `filter` (default value "-is:new"): card filter (same as typed in the browser window). Modify to restrict to a subset of your deck
- `also_export_last` (default value "false"): Also export the last review of a card? Set to true or false (case-sensitive) if set to true, the logfile will integrate a line where some of the items are left blank
- `start_date_range` (default value "false"), `end_date_range` (default value "false"): export date range. Only items with Date1 in the range will be compared. Examples: "2017-01-24", "2017-01", "2017", false
