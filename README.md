# Fuck MS Proxy

This is a simple web service to fix an issue which is annoying the hell out of me. 

MS have broken their outlook server by restricting the clients which are able to access it. 
[See here for further info](https://learn.microsoft.com/en-us/answers/questions/5529826/ics-calendar-subscription-not-working-has-the-feat).

To deal with this i'm going to have to write myself a proxy service which will take a url and then replace the agent header before sending the request off to outlook.

## Usage

take your ICal subscription address URL and remove the `https://`

example:
`https://outlook.office365.com/owa/calendar/12341234123412341234123412341234@outlook.com/1234123412341234123412341234123412341234123412341234/calendar.ics`

becomes
`outlook.office365.com/owa/calendar/12341234123412341234123412341234@outlook.com/1234123412341234123412341234123412341234123412341234/calendar.ics`

then pass that to this servers `/outlook/` endpoint as below. 

http://127.0.0.1:8000/outlook/outlook.office365.com/owa/calendar/12341234123412341234123412341234@outlook.com/1234123412341234123412341234123412341234123412341234/calendar.ics
