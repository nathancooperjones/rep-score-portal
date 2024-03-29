All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project uses [Semantic Versioning](http://semver.org/).

# [0.16.2] - 2024-01-26
### Changed
 - Upgraded Streamlit to version ``1.30.0``
 - Upgraded Streamlit-Authenticator to version ``0.3.1``

# [0.16.1] - 2023-12-07
### Changed
 - Upgraded Streamlit to version ``1.29.0``
### Fixed
 - Bug with overlapping labels in the "Explore Your Data" color map

# [0.16.0] - 2023-11-03
### Changed
 - Upgraded Streamlit to version ``1.28.1``
 - Dockerfile to use Python 3.11 instead of 3.9
### Removed
 - DEI checklist questions when submitting an asset, now a link to a separate resource
 - Duplicate calls to pull down asset tracker spreadsheet after submitting an asset

# [0.15.2] - 2023-09-30
### Changed
 - Upgraded Streamlit to version ``1.27.0``

# [0.15.1] - 2023-09-03
### Added
 - "Presence Average (50)", "Prominence Average (10)", and "Stereotypes Average (40)" scores to the tooltip in the "Explore Your Data" overall scores color maps
### Changed
 - "Good, fair, and poor representation" wording to "high, medium, and low representation"
 - Checkbox in "Explore Your Data" page to a toggle
 - Upgraded Streamlit to version ``1.26.0``

# [0.15.0] - 2023-08-09
### Added
 - "Social Media Asset (Singular)" and "Social Media Package (Multiple)" to the content type dropdown when submitting and exploring the data of an asset
 - "Number of Assets" field to asset tracker spreadsheet when uploading
### Changed
 - Most every subsequent submission field when submitting an asset is now optional for all users
 - Allow for uploading multiple files for a single asset
 - Required fields when submitting an asset are now marked with a red asterisk
 - Specific error messages are now hidden to the end user and only displayed in the console
 - Renamed "Asset Filename" field to "Asset Filename(s)" in asset tracker spreadsheet
### Fixed
 - After submitting an asset, hitting the "Submit an Asset" button will now actually let you submit another asset

# [0.14.9] - 2023-07-21
### Changed
 - Upgraded Streamlit to version ``1.25.0``
### Fixed
 - ``pd.to_datetime`` warning

# [0.14.8] - 2023-07-19
### Added
 - Esso UK logo

# [0.14.7] - 2023-07-12
### Added
 - Mobil New Zealand logo

# [0.14.6] - 2023-05-17
### Changed
 - Upgraded Streamlit to version ``1.22.0``
### Fixed
 - Number of visible rows in the "Asset Information" tab table

# [0.14.5] - 2023-03-29
### Changed
 - Color scheme used across the entire Streamlit app
 - Upgraded Streamlit to version ``1.20.0``
### Fixed
 - Inadvertently hidden axis labels in the "Scores by Identity, Ad Level" plot on the "Explore Your Data" page
 - ``KeyError`` where ``seen_asset_before`` cannot be found in the Streamlit session state in certain edge cases

# [0.14.4] - 2023-02-13
### Added
 - BBDO Creative Compass logo option in the sidebar
### Changed
 - Upgraded Streamlit to version ``1.18.1``
 - Enabled static file hosting in Streamlit
### Fixed
 - Only displaying unique asset names as options in Step 0 of the "Submit an Asset" page

# [0.14.3] - 2023-02-07
### Fixed
 - The "Having issues logging in?" link will now properly disappear as soon as the user is logged in

# [0.14.2] - 2023-02-04
### Added
 - Timeouts and retries to Google Sheets connection attempts made in ``read_google_spreadsheet``
### Removed
 - Custom ``server.runOnSave``, ``server.enableCORS``, ``server.enableXsrfProtection``, and ``runner.fastReruns`` settings set in ``.streamlit/config.toml``

# [0.14.1] - 2023-02-03
### Changed
 - Upgraded the version of ``streamlit_authenticator`` used to ``>=0.2.0``, restructuring the ``secrets.toml`` file used in the backend of the application

# [0.14.0] - 2023-02-03
### Changed
 - Upload-related inputs for both the creative brief and asset within the "Submit an Asset" process have been color-coded to differentiate them from the other fields on the page
 - Required steps in the "Submit an Asset" process have been removed for select users listed in the ``asset_submission_inputs_optional`` group
 - "Rep Score Progress" plots on the "Explore Your Data" page now default to the portfolio view upon page load
 - View names for the "Rep Score Progress" plots on the "Explore Your Data" to be clearer
 - Streamlit version, now upgraded to ``1.17``
 - Code is now ``flake8-annotations`` compliant, with this requirement being added to the CI workflow along with import order and docstring linting
### Fixed
 - Ad names are now always displayed properly in each "Score Heatmap" plotted on the "Explore Your Data" page. Before, only about half the ad names were displayed due to a spacing bug

# [0.13.1] - 2023-01-04
### Fixed
 - "Asset Information" page to use updated column names

# [0.13.0] - 2022-12-22
### Added
 - Asset filters across all tabs in the "Explore Your Data" page, not just for the "Score Heatmap"
### Changed
 - Text box help cues to be actually helpful, rather than a template ``More info to come``
 - Colors used for good, fair, and poor representation in the "Score Heatmap" tab
 - Plots on the "Rep Score Progress" tab now have a set y-axis range from ``0`` to ``100``
 - Date picker colors to be more readable in the "Rep Score Progress" tab
 - Some language used during the asset submission process
### Fixed
 - Plots on the "Rep Score Progress" tab where the date submitted is the x-axis now includes all date values in the range, not just the ones where assets were submitted

# [0.12.0] - 2022-12-07
### Added
 - Page to view the uploaded notes and details about an assigned asset
 - Ability to go back to a previous page when submitting a new asset
 - Sections to add more fleshed out notes to each of the DEI Checklist questions, rather than just selecting a checkbox
### Changed
 - Having previously-submitted an asset no longer skips to Step 5 of the asset submission process, rather just autofills those answers
 - "Progress of All Available Assets" tab no longer shows brand, product, or content type - only version
 - Color of text areas for notes during the asset submission screens
 - Upgraded version of Streamlit used to ``1.15.2``

# [0.11.2] - 2022-10-05
### Fixed
 - "No Codeable Characters" filtered out of the Rep Score Progress plots
 - "Logout" button sets up for a successful next login done in the same session
 - Date sort for Rep Score Progress plots and Qualitative Notes
 - Font size for labels in color map plots

# [0.11.1] - 2022-09-29
### Fixed
 - "Refresh"/"Start over" and "Logout" buttons are now side-by-side on the sidebar
 - Added additional short-circuiting logic for users who are not signed in to not check for assigned assets

# [0.11.0] - 2022-09-29
### Added
 - Initial page before submitting an asset that allows a user to select a previously-uploaded asset whose details should be used to auto-fill and skip sections of the submission process
 - "Portfolio" view for the Rep Score Progress plot
 - Username displayed on the sidebar after login
### Changed
 - Downgraded both ``maxUploadSize`` and ``maxMessageSize`` from 12GB to 2GB
 - Upgraded Streamlit library version to ``streamlit~=1.13``
 - Renamed x-axis for progress plots from "Date Submitted Month Year" to "Date Submitted (Month)"
 - Size of version in sidebar
 - Faster loading times for users who have not been assigned any assets
### Fixed
 - Logout button now fully wipes previous session's data
 - Streamlit multi-select options have a larger max width
 - A Streamlit issue where tab selection would revert to the default for the first selection on the "Explore Your Data" page
 - Rep Score Progress data is now sorted by date submitted before plotting

# [0.10.9] - 2022-09-23
### Changed
 - Mars logo image

# [0.10.8] - 2022-09-20
### Added
 - "Video" content type options
### Fixed
 - Dynamic height for color map plots that scales as more data is added
 - Issue with OAuthLib library being vulnerable to DoS when attacker provides malicious IPV6 URI

# [0.10.7] - 2022-08-27
### Added
 - ExxonMobil logo option
### Fixed
 - Unnecessary trimmed ``Score`` value in ``Scores by Identity, Ad Level`` tooltip

# [0.10.6] - 2022-08-12
### Changed
 - Upgraded Streamlit library version to ``1.12.0``

# [0.10.5] - 2022-08-03
### Added
 - Introductory description of Score Heatmap plot colors and filters
### Changed
 - List of Content Type categories available

# [0.10.4] - 2022-07-29
### Added
 - Portfolio view of color maps, aggregating data from the color map data displayed
 - Helper functions ``insert_line_break`` and ``get_content_types`` to ``utils.py``
### Changed
 - Identity color maps are now available in an expander rather than triggered by a checkbox click
### Fixed
 - Order of x-axis for the Rep Score Progress plot
 - String values that overflowing out of the cells of identity color maps are now trimmed to fit entirely in the cell

# [0.10.3] - 2022-07-18
### Fixed
 - Updated sheet read for the project tracker Google spreadsheet
 - Tooltip in plots being visible over text

# [0.10.2] - 2022-07-15
### Added
 - Baseline column header in color map plots
 - Option to include baseline column in color map plots or not
### Changed
 - Replaced radio sidebar with tabs for the "Explore Your Data" page
 - Upgraded version of Streamlit to ``1.11.0``

# [0.10.1] - 2022-07-14
### Changed
 - Scores of "N/A" will not be displayed with a gray background in the "Explore Your Data" color maps
 - Displaying baseline in the "Explore Your Data" color maps
 - Added admin login group that can view all assets

# [0.10.0] - 2022-07-12
### Added
 - Multiple logo options depending on the login as specified in the ``secrets.toml`` file
 - Username uploaded to the asset tracking Google Spreadsheet
### Changed
 - Assets will only be displayed in the "Asset Overview" and "Explore Your Data" pages only if the asset is assigned to the user or the user uploaded the asset
 - Clarified messages displayed when no assets have been uploaded / assigned / completed yet on both the "Asset Overview" and "Explore Your Data" pages
### Removed
 - Sidebar during login screen
### Fixed
 - Uploading "Region(s) This Creative Will Air In" to the asset tracking Google Spreadsheet
 - ``plot_rep_score_progress`` will now show an error if no assets have been assigned / completed that have more than one version

# [0.9.5] - 2022-06-16
### Added
 - Initial help tooltips in various input spots
### Changed
 - Slight wording tweaks for inputs
### Removed
 - "Press Enter to apply" prompt in text inputs
### Fixed
 - Error message is displayed when all data is filtered out in "Asset Overview"
 - Color of the primary filter input in "Asset Overview" to be consistent with "Explore Your Data"

# [0.9.4] - 2022-06-16
### Fixed
 - Lemon/Milk font is now retrieved from an S3 bucket with proper CORS configuration

# [0.9.3] - 2022-06-15
### Changed
 - Optimized the application by only instantiating the authentication "once" during application startup
 - Storing authentication cookie details in ``secrets.toml`` for better security
### Fixed
 - Sidebar image spacing
### Removed
 - Unused ``st.session_state.important`` variable

# [0.9.2] - 2022-06-15
### Removed
 - JavaScript to refresh a page after resetting the ``asset_information`` variable
### Fixed
 - Flushing and seeking a closed file after upload in ``input_output.py``
 - ``maxMessageSize`` to match ``maxUploadSize`` in ``config.toml``
 - Streamlit server settings for HTTPS / SSL configuration

# [0.9.1] - 2022-06-15
### Removed
 - ``ssl-proxy`` code in favor of a traditional ACM + load balancer setup in AWS

# [0.9.0] - 2022-06-14
### Added
 - Filters for the "Asset Overview" page
 - Point of Contact input when submitting a new asset
 - Ability to submit a URL for the creative brief rather than uploading it directly
### Changed
 - Colors of file upload progress bars
 - Adding a new row to the asset tracking Google Spreadsheet does so as an append operation _without_ replacing existing rows
### Fixed
 - Specificity of HTTP(S) in ``ssl-proxy.sh``

# [0.8.1] - 2022-06-14
### Changed
 - Upload limit from ``2GB`` to ``16GB``
### Fixed
 - Lemon/Milk font served over HTTPS
 - ``ValueError`` when uploading the asset to S3
 - Better handling of ``BytesIO`` file uploads to trigger garbage collection earlier
 - Better hiding of title anchors

# [0.8.0] - 2022-06-10
### Added
 - Docstrings and type hints to all functions
 - Ability to upload a creative brief to S3 when submitting a new asset
 - Ability to provide a URL to an asset rather than having to upload an asset when submitting a new asset
### Changed
 - Broke up ``upload_file_and_update_tracker`` into two separate functions: ``upload_file_to_s3`` and ``append_new_row_in_asset_tracker``
 - Cached color map dataset in ``explore_your_data.py``
 - General code cleanup
### Fixed
 - Error is now correctly displayed when filtered data has zero rows in ``plot_color_maps``

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
 - Initial repo setup
