# AWAvenue Geosite

An independent converter that compiles [AWAvenue Ads Rule](https://github.com/TG-Twilight/AWAvenue-Ads-Rule) into an Xray-compatible GeoSite `awavenue.dat` file.

This project is not affiliated with, endorsed by, or officially associated with the AWAvenue Ads Rule project or its maintainers.

The conversion is automatically performed by GitHub Actions. The workflow periodically checks the upstream rule file and updates the `latest` GitHub Release when changes are detected.

The generated release contains:

* `awavenue.dat` — compiled GeoSite database
* `awavenue.dat.sha256` — SHA-256 checksum of the database

Except for the upstream AWAvenue rule data, the source code of this repository is licensed under the MIT License. The upstream AWAvenue Ads Rule and derived data remain subject to their applicable upstream licensing terms.
