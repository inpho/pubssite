use pubs;

CREATE EVENT update_gender_event
	ON SCHEDULE
		EVERY 1 WEEK
	DO
		CALL Update_Gender();

SHOW EVENTS;