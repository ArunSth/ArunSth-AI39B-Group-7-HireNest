USE `HireNest`;

INSERT INTO `Job_Seekers` (`User_id`, `Profile_completion_percentage`)
SELECT u.`User_id`, 0.0
FROM `User` u
LEFT JOIN `Job_Seekers` js ON js.`User_id` = u.`User_id`
WHERE u.`Role` = 'job_seeker'
  AND js.`Seekers_id` IS NULL;
