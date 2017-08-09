# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.


from bson.objectid import ObjectId
import json
import web
from inginious.frontend.webapp.pages.course_admin.utils import INGIniousSubmissionAdminPage


class CourseReplaySubmissions(INGIniousSubmissionAdminPage):
    """ Replay operation management """

    def POST_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        course, _ = self.get_course_and_check_rights(courseid, allow_all_staff=False)
        user_input = web.input(tasks=[], aggregations=[], users=[])

        if "submission" in user_input:
            # Replay a unique submission
            submission = self.database.submissions.find_one({"_id": ObjectId(user_input.submission)})
            if submission is None:
                raise web.notfound()

            web.header('Content-Type', 'application/json')
            self.submission_manager.replay_job(course.get_task(submission["taskid"]), submission)
            return json.dumps({"status": "waiting"})
        else:
            # Replay several submissions, check input
            tasks = course.get_tasks()
            error = False
            msg = _("Selected submissions were set for replay.")
            for i in user_input.tasks:
                if i not in tasks.keys():
                    msg = _("Task with id {} does not exist !").format(i)
                    error = True

            if not error:
                # Load submissions
                submissions, _ = self.get_selected_submissions(course, user_input.filter_type, user_input.tasks, user_input.users, user_input.aggregations, user_input.type)
                for submission in submissions:
                    self.submission_manager.replay_job(tasks[submission["taskid"]], submission)

            return self.show_page(course, web.input(), msg, error)

    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        course, _ = self.get_course_and_check_rights(courseid, allow_all_staff=False)
        return self.show_page(course, web.input())

    def show_page(self, course, user_input, msg="", error=False):
        # Load task list
        tasks, user_data, aggregations, tutored_aggregations,\
        tutored_users, checked_tasks, checked_users, show_aggregations = self.show_page_params(course, user_input)

        return self.template_helper.get_renderer().course_admin.replay(course,
                                                                         tasks, user_data, aggregations,
                                                                         tutored_aggregations, tutored_users,
                                                                         checked_tasks, checked_users,
                                                                         show_aggregations, msg, error)
