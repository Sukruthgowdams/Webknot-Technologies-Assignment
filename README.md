README:
This Project is Campus Event Management System , that is built as per the assignment given:
The system allows students to sign up, log in, browse events, and register for the ones they are interested in. Admins can create, update, or delete events and keep track of how many students have registered.
So , this project is is build using Python using flask which handles the authentication, event management, and storing all data in SQLite
The front end is done by HTML and CSS and JS

So everything is done as per assignment and I have also added all the files required in zip along with code of project
But additionally I HAVE DEPLOYED ITTT SUCCESSFULLY!!!!!!
ACCESS THE PROJECT USING LINK HERE :
https://webknot-technologies-assignment.onrender.com/ui 
This was deployed using RENDER

U CAN CHECK THE FUCTIONALITY IN THE WEBSITE!!!

To run locally:
Install everything needed.
pip install -r requirements.txt
initialize: python app.py
so this should create SQLite DB
and run flask server : Flask RUN

SO RUN CURL Commands in Cmd with respect to the url:
Example:

CURL POST:  curl -X POST https://webknot-technologies-assignment.onrender.com/events -H "Content-Type: application/json" -d "{\"title\":\"Hackathon\",\"event_type\":\"Workshop\",\"start_time\":\"2025-09-07T10:00:00\",\"end_time\":\"2025-09-07T16:00:00\"}"

CURL GET (EVENTS): curl -X GET https://webknot-technologies-assignment.onrender.com/events


CURL PUT( UPDATE) : curl -X PUT https://webknot-technologies-assignment.onrender.com/events/1 \
-H "Content-Type: application/json" \
-d "{\"title\":\"Updated Hackathon\",\"event_type\":\"Workshop\",\"start_time\":\"2025-09-07T11:00:00\",\"end_time\":\"2025-09-07T17:00:00\"}"


And so on.. You can use similar CURL commands for GET, PUT, and DELETE requests as per the API endpoints
DO READ THE DESIGN DOC.
So my personally,
I gained hands-on experience in building a full-stack web application. I understood how Flask can handle authentication, routing, and database operations
And also I im not attaching the screenshots of outputs, because u can check it on the link itself
but ill we attaching the cmd prompts.
THANK YOU FOR THIS Opportunity .


Prototype Code
•	Include your full project folder:
•	CampusEventManagement/
•	├── app.py (or main backend file)
•	├── requirements.txt
•	├── templates/
•	│   └── index.html
•	├── static/
•	│   ├── css/
•	│   └── js/
•	├── README.md
└── database.db (if using SQLite)
