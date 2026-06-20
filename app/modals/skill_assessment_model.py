"""
Skill Assessment Model
======================
Handles all DB operations for the Skill Assessment feature.

Tables used (already created by base_model.create_all()):
    - Skills_Assessments
    - Assessment_Questions
    - Seeker_Assessment_Attempts

This file follows the same pattern as the other *_model.py files
in app/modals (raw pymysql via app.database.get_connection()).
"""

import json
from datetime import datetime, timedelta
from app.database import get_connection


# 7-day cooldown after each completed attempt (per Acceptance Criteria)
COOLDOWN_DAYS = 7
# Minimum % score to be considered "Passed" -> earns verified badge
PASS_PERCENTAGE = 70.0


class SkillAssessmentModel:
    # ----------------------------------------------------------------------
    #  ASSESSMENT MANAGEMENT
    # ----------------------------------------------------------------------
    @staticmethod
    def get_all_assessments():
        """Return all active assessments with question counts."""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT  s.`Assessment_id`,
                            s.`Title`,
                            s.`Description`,
                            s.`Duration_minutes`,
                            s.`Total_marks`,
                            s.`Is_active`,
                            s.`Created_at`,
                            (SELECT COUNT(*) FROM `Assessment_Questions` q
                             WHERE q.`Assessment_id` = s.`Assessment_id`) AS question_count
                    FROM    `Skills_Assessments` s
                    WHERE   s.`Is_active` = TRUE
                    ORDER BY s.`Title` ASC
                    """
                )
                return cur.fetchall() or []
        finally:
            conn.close()

    @staticmethod
    def get_assessment_by_id(assessment_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM `Skills_Assessments` WHERE `Assessment_id`=%s",
                    (assessment_id,),
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def create_assessment(title, description, duration_minutes, total_marks):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO `Skills_Assessments`
                        (`Title`, `Description`, `Duration_minutes`, `Total_marks`, `Is_active`)
                    VALUES (%s, %s, %s, %s, TRUE)
                    """,
                    (title, description, duration_minutes, total_marks),
                )
                conn.commit()
                return cur.lastrowid
        except Exception as e:
            print(f"[SkillAssessmentModel.create_assessment] {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    # ----------------------------------------------------------------------
    #  QUESTIONS
    # ----------------------------------------------------------------------
    @staticmethod
    def get_questions_for_assessment(assessment_id, include_correct=False):
        """
        Return questions of a given assessment.
        `include_correct=False` (default) hides the correct answer from
        the candidate while taking the test.
        """
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT `Question_id`, `Assessment_id`, `Question_text`,
                           `Question_type`, `Options_json`, `Correct_answer`, `Marks`
                    FROM   `Assessment_Questions`
                    WHERE  `Assessment_id` = %s
                    ORDER BY `Question_id` ASC
                    """,
                    (assessment_id,),
                )
                rows = cur.fetchall() or []
                for r in rows:
                    raw_opts = r.get("Options_json")
                    if raw_opts:
                        try:
                            r["options"] = (
                                json.loads(raw_opts)
                                if isinstance(raw_opts, (str, bytes, bytearray))
                                else raw_opts
                            )
                        except Exception:
                            r["options"] = []
                    else:
                        r["options"] = []
                    if not include_correct:
                        r["Correct_answer"] = None
                return rows
        finally:
            conn.close()

    @staticmethod
    def add_question(assessment_id, question_text, options_list,
                     correct_answer, marks=1, question_type="mcq"):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO `Assessment_Questions`
                        (`Assessment_id`, `Question_text`, `Question_type`,
                         `Options_json`, `Correct_answer`, `Marks`)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        assessment_id,
                        question_text,
                        question_type,
                        json.dumps(options_list) if options_list else None,
                        correct_answer,
                        marks,
                    ),
                )
                conn.commit()
                return cur.lastrowid
        except Exception as e:
            print(f"[SkillAssessmentModel.add_question] {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    # ----------------------------------------------------------------------
    #  ATTEMPTS
    # ----------------------------------------------------------------------
    @staticmethod
    def get_attempts_for_seeker(seekers_id):
        """All attempts for the seeker, latest first, joined with assessment title."""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT  a.`Attempt_id`, a.`Assessment_id`, a.`Score`,
                            a.`Status`, a.`Started_at`, a.`Submitted_at`,
                            s.`Title`, s.`Total_marks`, s.`Duration_minutes`
                    FROM    `Seeker_Assessment_Attempts` a
                    JOIN    `Skills_Assessments` s
                              ON a.`Assessment_id` = s.`Assessment_id`
                    WHERE   a.`Seekers_id` = %s
                    ORDER BY a.`Submitted_at` DESC, a.`Attempt_id` DESC
                    """,
                    (seekers_id,),
                )
                return cur.fetchall() or []
        finally:
            conn.close()

    @staticmethod
    def get_latest_attempt(seekers_id, assessment_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM   `Seeker_Assessment_Attempts`
                    WHERE  `Seekers_id` = %s AND `Assessment_id` = %s
                    ORDER BY `Attempt_id` DESC
                    LIMIT 1
                    """,
                    (seekers_id, assessment_id),
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def can_retake(seekers_id, assessment_id):
        """
        Returns (allowed: bool, next_available_at: datetime | None).
        Implements the 7-day cooldown stated in the Acceptance Criteria.
        """
        last = SkillAssessmentModel.get_latest_attempt(seekers_id, assessment_id)
        if not last:
            return True, None
        submitted_at = last.get("Submitted_at")
        if not submitted_at:
            # An unfinished attempt -- let the user finish it (no cooldown yet)
            return True, None
        next_available = submitted_at + timedelta(days=COOLDOWN_DAYS)
        if datetime.now() >= next_available:
            return True, None
        return False, next_available

    @staticmethod
    def start_attempt(seekers_id, assessment_id):
        """Create a new attempt row with status 'in_progress'. Returns attempt_id."""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO `Seeker_Assessment_Attempts`
                        (`Assessment_id`, `Seekers_id`, `Score`,
                         `Status`, `Started_at`)
                    VALUES (%s, %s, 0, 'in_progress', NOW())
                    """,
                    (assessment_id, seekers_id),
                )
                conn.commit()
                return cur.lastrowid
        except Exception as e:
            print(f"[SkillAssessmentModel.start_attempt] {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def submit_attempt(attempt_id, answers_dict):
        """
        Grade the attempt.

        answers_dict: {question_id (int|str) : chosen_answer (str)}

        Returns a result dict:
            { 'score': float (percentage),
              'obtained': int,
              'total': int,
              'passed': bool,
              'correct_count': int,
              'total_questions': int }
        """
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # 1) Locate the attempt
                cur.execute(
                    "SELECT * FROM `Seeker_Assessment_Attempts` WHERE `Attempt_id`=%s",
                    (attempt_id,),
                )
                attempt = cur.fetchone()
                if not attempt:
                    return None

                assessment_id = attempt["Assessment_id"]

                # 2) Pull all questions (with the correct answer)
                cur.execute(
                    """
                    SELECT `Question_id`, `Correct_answer`, `Marks`
                    FROM   `Assessment_Questions`
                    WHERE  `Assessment_id` = %s
                    """,
                    (assessment_id,),
                )
                questions = cur.fetchall() or []

                obtained = 0
                total = 0
                correct_count = 0
                for q in questions:
                    total += q["Marks"] or 1
                    qid = str(q["Question_id"])
                    user_ans = (answers_dict.get(qid) or
                                answers_dict.get(q["Question_id"]) or "").strip()
                    correct = (q["Correct_answer"] or "").strip()
                    if user_ans and user_ans.lower() == correct.lower():
                        obtained += q["Marks"] or 1
                        correct_count += 1

                percentage = round((obtained / total) * 100.0, 2) if total > 0 else 0.0
                passed = percentage >= PASS_PERCENTAGE
                status = "passed" if passed else "failed"

                # 3) Persist the final result
                cur.execute(
                    """
                    UPDATE `Seeker_Assessment_Attempts`
                    SET    `Score`        = %s,
                           `Status`       = %s,
                           `Submitted_at` = NOW()
                    WHERE  `Attempt_id`   = %s
                    """,
                    (percentage, status, attempt_id),
                )
                conn.commit()

                return {
                    "score": percentage,
                    "obtained": obtained,
                    "total": total,
                    "passed": passed,
                    "correct_count": correct_count,
                    "total_questions": len(questions),
                    "status": status,
                }
        except Exception as e:
            print(f"[SkillAssessmentModel.submit_attempt] {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    # ----------------------------------------------------------------------
    #  BADGES (for profile display)
    # ----------------------------------------------------------------------
    @staticmethod
    def get_passed_badges(seekers_id):
        """
        Return one row per assessment that the seeker has PASSED,
        keeping only the highest score.  Used for the verified-badge
        display on the seeker profile.
        """
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT  s.`Assessment_id`, s.`Title`,
                            MAX(a.`Score`) AS best_score
                    FROM    `Seeker_Assessment_Attempts` a
                    JOIN    `Skills_Assessments` s
                              ON a.`Assessment_id` = s.`Assessment_id`
                    WHERE   a.`Seekers_id` = %s
                      AND   a.`Status`     = 'passed'
                    GROUP BY s.`Assessment_id`, s.`Title`
                    ORDER BY best_score DESC
                    """,
                    (seekers_id,),
                )
                return cur.fetchall() or []
        finally:
            conn.close()

    # ----------------------------------------------------------------------
    #  ONE-TIME SEED  (called from app/__init__.py, idempotent)
    # ----------------------------------------------------------------------
    @staticmethod
    def seed_default_assessments():
        """
        Populate the DB with a few popular skill assessments
        (Python, JavaScript, Communication, SQL) the first time the
        app runs.  Idempotent -- it only inserts when the table is empty.
        """
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS cnt FROM `Skills_Assessments`")
                row = cur.fetchone()
                if row and row["cnt"] > 0:
                    return  # already seeded
        finally:
            conn.close()

        seed_data = [
            {
                "title": "Python Fundamentals",
                "description": "Test your knowledge of Python basics: syntax, data types, control flow and built-in functions.",
                "duration": 15,
                "questions": [
                    ("Which keyword is used to define a function in Python?",
                     ["def", "function", "fun", "define"], "def"),
                    ("What is the output of `print(type([]))`?",
                     ["<class 'list'>", "<class 'tuple'>", "<class 'dict'>", "<class 'set'>"], "<class 'list'>"),
                    ("Which of the following is an immutable data type?",
                     ["list", "dict", "tuple", "set"], "tuple"),
                    ("How do you start a single-line comment in Python?",
                     ["//", "#", "/*", "--"], "#"),
                    ("What does the `len()` function return for a string?",
                     ["Number of words", "Number of characters", "Bytes used", "Memory address"],
                     "Number of characters"),
                ],
            },
            {
                "title": "JavaScript Essentials",
                "description": "Core JavaScript concepts: variables, scope, functions and DOM basics.",
                "duration": 15,
                "questions": [
                    ("Which keyword declares a block-scoped variable?",
                     ["var", "let", "static", "func"], "let"),
                    ("`typeof null` returns?",
                     ["'null'", "'object'", "'undefined'", "'number'"], "'object'"),
                    ("Which method converts a JSON string to an object?",
                     ["JSON.stringify()", "JSON.parse()", "JSON.toObject()", "Object.fromJSON()"], "JSON.parse()"),
                    ("`===` checks for ____ ?",
                     ["Value only", "Reference only", "Value and Type", "Truthiness"], "Value and Type"),
                    ("Arrow functions do NOT have their own ___ ?",
                     ["arguments", "this", "Both arguments and this", "None"], "Both arguments and this"),
                ],
            },
            {
                "title": "Communication Skills",
                "description": "Evaluate professional written and verbal communication.",
                "duration": 10,
                "questions": [
                    ("Active listening primarily means:",
                     ["Waiting your turn to talk",
                      "Fully concentrating, understanding and responding",
                      "Nodding throughout the conversation",
                      "Repeating the speaker word-for-word"],
                     "Fully concentrating, understanding and responding"),
                    ("Best practice when sending a professional email:",
                     ["No subject is fine if the body is clear",
                      "Use a clear subject line and concise message",
                      "Use only capital letters for emphasis",
                      "Skip the greeting"],
                     "Use a clear subject line and concise message"),
                    ("Non-verbal communication includes:",
                     ["Tone of voice", "Body language", "Facial expressions", "All of the above"],
                     "All of the above"),
                    ("'Empathy' in communication means:",
                     ["Agreeing with everything someone says",
                      "Understanding and sharing the feelings of another",
                      "Solving the other person's problems",
                      "Avoiding difficult conversations"],
                     "Understanding and sharing the feelings of another"),
                    ("Which is an example of constructive feedback?",
                     ["'Your report was bad.'",
                      "'You always make mistakes.'",
                      "'The intro is strong; the data section could use clearer charts.'",
                      "'Just redo it.'"],
                     "'The intro is strong; the data section could use clearer charts.'"),
                ],
            },
            {
                "title": "SQL Basics",
                "description": "Querying relational databases: SELECT, JOIN, GROUP BY and constraints.",
                "duration": 15,
                "questions": [
                    ("Which SQL clause filters rows BEFORE grouping?",
                     ["HAVING", "WHERE", "ORDER BY", "GROUP BY"], "WHERE"),
                    ("Which JOIN returns only matching rows from both tables?",
                     ["LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "FULL JOIN"], "INNER JOIN"),
                    ("PRIMARY KEY columns are:",
                     ["Always NULLABLE", "UNIQUE and NOT NULL", "Allowed to repeat", "Optional in every table"],
                     "UNIQUE and NOT NULL"),
                    ("Which aggregate function counts non-NULL values?",
                     ["SUM", "AVG", "COUNT", "MAX"], "COUNT"),
                    ("Which statement removes ALL rows but keeps the table?",
                     ["DROP TABLE", "DELETE TABLE", "TRUNCATE TABLE", "REMOVE TABLE"], "TRUNCATE TABLE"),
                ],
            },
        ]

        for sd in seed_data:
            total_marks = len(sd["questions"])
            aid = SkillAssessmentModel.create_assessment(
                sd["title"], sd["description"], sd["duration"], total_marks
            )
            if aid:
                for qtext, options, correct in sd["questions"]:
                    SkillAssessmentModel.add_question(
                        aid, qtext, options, correct, marks=1, question_type="mcq"
                    )
        print("[SkillAssessmentModel] Seeded default assessments.")
