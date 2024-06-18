_The Space Devs_ Launch Library 2 API:   
https://ll.thespacedevs.com/2.2.0/swagger/#/launch/launch_list
# Launch Tracker

## Description of the Project

The Launch Tracker web application allows users to view and collect rocket launch mission data by creating a profile and browsing launch data. It is intended for any and all rocket and outer space enthusiasts. By using the Launch Tracker, a user is able to collect launches of a wide variety or specificity. This gives them a quick, user-friendly catalog of launches with consistently updating data.

![Class Diagram](/Planning_Files/Launch_Collection_DB_Diagram.png)

## User Stories

- As an outer-space enthusiast, I want to see the who, what, when, and where of everything launching out of our atmosphere, from organizations all around the globe.
- As a shareholder of aerospace companies, I want to be able to quickly track and anticipate what my invested money is doing.

## Setup

Instructions on how to use the Launch Tracker and make modifications.

### Prerequisites

- Web browser: make sure you have a current web browser installed such as Google Chrome, Microsoft Edge, or Mozilla Firefox.
- Internet connection: the Launch Tracker uses current data so make sure you are online.
- Visual Studios (VS) Code: you will need VS Code or an equivalent coding program to make additions to the Launch Tracker. 
- Git Bash or Ubuntu Terminal: make sure you have a functioning terminal.

### Running the Application in Visual Studios (VS) Code

Follow these steps to get your application running within VS Code:

1. Open your terminal and navigate to the directory where you cloned or downloaded the project.
2. Create and activate a virtual environment: 
	1. Ubuntu:`python -m venv` then  `source venv/bin/activate`
	2. Git Bash: `python -m venv` then `source venv/Scripts/activate`
3. The `requirements.txt` file has all of the libraries required to run the Launch Tracker; run it:
	1. `pip install -r requirements.txt`
4. Then start the server using Flask in debug mode:
	1. `export FLASK_DEBUG=1`
	2. `flask run`   
1. Open VS Code
2. Select "Open Folder" and navigate to the directory with your venv and project files.
3. After the project opens, wait for VS Code to index the files and set up the project.
4. Troubleshoot any version discrepancies that may arise.
4. Make modifications as you see fit on your cloned addition, and then I look forward to your push requests!

## Technologies Used

- Python (3.10.2)
- Flask (3.0.3)
- SQLAlchemy (2.0.29)
- WTForms (3.1.2)
- see `requirements.txt` for complete list

## Demo

Include screenshots or GIFs that show your application in action. Use tools like [Giphy Capture](https://giphy.com/apps/giphycapture) to record a GIF of your application.

![Application Screenshot](path/to/your/screenshot.png)

## Future Work

- The Launch Tracker will get more focused and compartmentalized with its data. Launches will be sorted more clearly into categories, such as, "upcoming", "previous", "between this and that date", etc.
- A social element will be added, i.e. sharing collections with other users, adding friendship connections, sending launches or other data to other users. Perhaps a forum-style discussion area will be added, too.
- Currently, the main details for each launch are retrieved and stored, but the API has a wealth of information about every detail of every launch. In the future, all of it may be accessed, for the ultra-curious space pioneer.

## Resources

List resources such as tutorials, articles, or documentation that helped you during the project.

- [Bootstrap Docs](https://getbootstrap.com/docs/5.3/getting-started/introduction/)
- [Stackoverflow (various)](https://www.stackoverflow.com)

## Team Members

- **Jonathan Jones** - Project Lead, Lead Developer.
- **JJ** - Head of Styling and UI.

## Thanks

Express gratitude towards those who provided help, guidance, or resources:

- Thank you to Raymond Maroun for continuous support and guidance.
- A special thanks to all teammates for their dedication and teamwork.