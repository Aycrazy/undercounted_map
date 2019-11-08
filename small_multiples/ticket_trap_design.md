RE: Using Ticket Trap as a Template for our Partner Maps
***

<u>Purpose</u>: Learn what software architecture, programming languages, libraries, storage (dbs -- if any) were used to create the Ticket Trap webpage, so that we can use it for our own purposes.

<u>Source 1</u>: ["The Ticket Trap: Front to Back"](https://www.propublica.org/nerds/the-ticket-trap-news-app-front-to-back-david-eads-propublica-illinois)

<u>Main Idea</u>: "Managing and minimizing maintenance debt is particularly important to small organizations that hope to do ambitious digital work with limited resources. If you’re at a small organization, or are just looking to solve similar problems, read on: These tools might help you, too."

<u>Key Takeaways</u>: 

##### Design
- The Ticket Trap focuses on wards, why?
  - Primary political division and most relevant admin geography
  - <b>Consideration</b>: what is the primary division for our purposes?
    - Primary --> most important to see immediately and will fulfill > 60% of use cases
- This decision led to the design of having the homepag ase an animated, sortable list that highlight wards
- Small multiples ENCOURAGE comparison across the selected geography -- for our purposes this is important for organizations that serve "non-bondaried" constituency or client populations
- At the top of the Ticket Trap's page, they have different topics that, when clicked on provide a explanation of its importance/implications and sorts the small multiples by where the topic has most severe implications (example: "What happens if you don't pay a ticket?")
  - Something to consider "Even though many people from vulnerable communities are affected by tickets in Chicago, they’re not always familiar with the jargon, which puts them at a disadvantage when trying to defend themselves. Empowering them by explaining some basic concepts and terms was an important goal for us."
- Below explanation of terms, there are "small cards" for a quick "skim and dive" to make visual comparisons across wards on demographic info, this can be customized by the user
- For more abundant and specific ward-based information there is a "click-through" page dedicated to that ward
- Decisions about which visualizations to use are based on highlighting information, in this case systemic injustices
  
##### Architecture
High Level:
- Front-End: Static Site generator -- GatsbyJs
  - Queries data, fills returning data into a template built in React (js framework)
- Deployment and Dev tools: Grunt-based command line interface

- Data Management: Postgres (+Postgis Extension)
  - Use GNU Make (makefile) to build the database,will also build map tiles and upload the tiels to MapBox
  - Query Layer -- Hasura - provides a GraphQL (query language for API) wrapper to Postgres so GatsbyJs can query
- Search and dynamic services: search is handeled by a AWS Lambda function managed with Serverless "ferries" simple queries to an RDS db

<i>Front End Site Generator</i>
- GatsbyJs bundles templates and UI together w/ React components
  - Small code components that bundle data and interactivity together

<i> Data Mgmt </i>
- Hasura (high level) - allows user to query postgres db with Json-esque queries (using Graphql)
- Postgres required
  
<i> Data Loading </i>
- GNU Make was the workhorse, but maybe could use a different tool

<i>Analysis and Processing for Display</i>
- Using pre-made sql queries, "take the enormous database of tickets and crunch it down into smaller tables that aggregate combinations of variables, then run all analysis against those tables."

<i>Geocoding</i>
- Geocodio
- Could use Degauss or MAI/DIME if necessary

<i>Dynamic Search with Microservices</i>
- Mapbox Autocomplete Geocoder to allow searching without spinning up services, AWS LAMBDA - tiny API, Amazon Aurora Database and Serverless connection
  - "Mapbox provides suggested addresses, and when the user clicks on one, we dispatch a request to the back-end service with the latitude and longitude, which are then run through a simple point-in-polygon query to determine the ward"
  - Use python to create and execute query against db, useing "records" library

<u>Other Notes:</u>
- Working backward help with db structure
  - "I simply wrote queries that described the way I wanted the data to be structured for the front end and worked backward to create the relational database structures to fulfill those queries."