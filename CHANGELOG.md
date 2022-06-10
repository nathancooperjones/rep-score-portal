All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project uses [Semantic Versioning](http://semver.org/).

# [0.7.0] - 2022-06-10
### Changed
 - Simplified SSL / HTTPS support for the application using ``ssl-proxy``
### Removed
 - Nginx logic in favor of ``ssl-proxy``

# [0.6.0] - 2022-06-08
### Added
 - SSL / HTTPS support for the application when running on an EC2 instance using NGINX
 - Questions for country of origin when uploading an asset
 - Notes section for every DEI checklist as a way to forego checking every box on the page to continue
 - Application version to the sidebar
### Changed
 - Refactored code so each major section has its own code file (finally)
### Removed
 - Summary of final two DEI checklists after asset upload

# [0.5.2] - 2022-06-07
### Added
 - Captions explaining that all checkboxes must be checked to continue to the next page when uploading a new asset
### Changed
 - Secrets and credentials are now stored in ``secrets.toml``
 - Banner is now shown even when logged out
 - Upgraded to ``streamlit==1.10.0``
### Removed
 - Library dependency for ``streamlit-aggrid``

# [0.5.1] - 2022-06-05
### Changed
 - Refactored custom CSS code to be global throughout the application
 - Current page when uploading an asset is now bolded
 - Asset name is not shown a second time when viewing the asset tracking expander
### Fixed
 - Button CSS for cross-browser compatibility

# [0.5.0] - 2022-06-02
### Added
 - Streamlit configuration in ``config.toml``
 - Streamlit page title and icon
 - Note in color map about visualizing different versions of the same asset
 - Progress bar images for every asset upload page
 - Progress bar visualization displayed once the asset is uploaded
 - Footer logic to display a floating image in ``footer.py``
 - Managed requirements
### Changed
 - Logos, branding, and theming used throughout the application
 - Split data exploration into separate "pages"
 - Text area boxes CSS
 - Radio buttons to select pages into custom buttons
### Fixed
 - Naming in ``Dockerfile``
 - Logic for clearing the radio selection on application startup
 - Lemon/Milk font CSS logic to work cross-browser
 - Refined CSS for progress bars to not rely on dynamically-generated CSS in Streamlit

# [0.4.0] - 2022-06-02
### Added
 - Additional input fields when uploading a new asset: asset name, brand, product, content type, version, and notes
 - Additional fields to the asset tracking Google Spreadsheet: asset name, brand, product, content type, version, and notes
 - Progress page indications in the sidebar when uploading a new asset
 - Asset tracking page now shows progress bar visualization instead of the raw asset tracking table
 - Lemon/Milk font for headers
### Changed
 - Asset filename in S3 includes timestamp
 - Uploading an asset flow is now broken up into separate "pages"

# [0.3.0] - 2022-06-02
### Added
 - Timestamps to uploads in asset tracking Google Spreadsheet
 - Summary of final two DEI checklists after asset upload
 - Additional filters for the color map: content type and date submitted
 - Scores text on top of squares in the color map
 - Progress chart of rep scores over time or content type
 - Qualitative notes view
 - Colors to asset tracker to visually show progress
### Changed
 - Refined language used throughout application
### Removed
 - AgGrid table view of datasets

# [0.2.0] - 2022-06-02
### Added
 - Login screen using ``streamlit_authenticator``
 - Logo in sidebar
 - S3 connection to upload assets to
 - Visualization to plot a color map of rep scores (total and broken up by identity) with filters
 - Checkboxes for DEI checklist when uploading a new asset
### Changed
 - Refactored how we read Google Spreadsheets

# [0.1.0] - 2022-06-02
### Added
 - Prototype Streamlit app

# [0.0.0] - 2022-06-02
### Added
 - Initial repo stup