import grp

from jupyterhub.handlers import BaseHandler
from ltiauthenticator import LTIAuthenticator
from tljh.normalize import generate_system_username
from tljh.user import ensure_user

import os
import subprocess
import shlex
import hashlib


class StudipAuthenticator(LTIAuthenticator):
    username_key = "user_id"

    _instructor_roles = ["Instructor", "Administrator", "Staff"]
    _course_id = ""

    def is_instructor(self, user_roles):
        return any([role in user_roles for role in self._instructor_roles])

    async def authenticate(  # noqa: C901
            self, handler: BaseHandler, data: dict = None
    ) -> dict:
        result = await super().authenticate(handler, data)

        user_roles = handler.get_argument("roles", "Learner").split(",")
        self._course_id = handler.get_argument("context_id", None)
        course_name = handler.get_argument("context_title", None)
        user_id = handler.get_argument("user_id", None)

        # Do nothing when course id and user id are not provided
        if self._course_id and user_id:
            # # For instructors replace name with composition of course id and user id
            # if self.is_instructor(user_roles):
            #     result["name"] = f"{self._course_id}-{user_id}"
            #
            # self.log.debug(f"user-name: {result['name']}")

            # Ensure user exists. TODO: Move these functions to custom spawner to prevent this
            system_username = generate_system_username("jupyter-" + result["name"])
            ensure_user(system_username)

            # Create course workspace if not existing
            course_dir = f"/srv/data/courses/{self._course_id}"
            self.log.debug(f"course-dir: {course_dir}")
            if not os.path.exists(course_dir):
                os.makedirs(course_dir)

            # # Create courses dir in home
            # home_courses_path = os.path.expanduser(f"~{system_username}/courses/")
            # if not os.path.exists(home_courses_path):
            #     os.mkdir(home_courses_path, 0o770)
            #
            # # Change group to user
            # user_gid = grp.getgrnam(system_username).gr_gid
            # os.chown(home_courses_path, -1, user_gid, follow_symlinks=False)

            # # Remove old symlink
            # course_name = course_name if course_name else self._course_id
            # home_course_path = f"{home_courses_path}/{course_name}"
            # if os.path.exists(home_course_path):
            #     os.remove(home_course_path)
            #
            # # Add symlink of course workspace to home directory
            # os.symlink(course_dir, home_course_path)
            # self.log.debug(f"home-link: {home_courses_path}")

            try:
                # Create course linux group with write permissions for course workspace if not existing
                # Unix allows group ids up to 32 chars
                course_group = f"jupyter-c-{self._course_id}"[:32]
                self.log.debug(f"course-group: {course_group}")
                subprocess.check_call(["groupadd", "-f", course_group])

                # Set course workspace mode:
                # Owner, group: read, write, execute; other: read, execute
                subprocess.check_call(["chmod", "-R", "775", course_dir])

                # Set group for course workspace
                subprocess.check_call(["chgrp", "-Rf", course_group, course_dir])

                # If instructor add user to course group
                if self.is_instructor(user_roles):
                    subprocess.check_call(["gpasswd", "--add", system_username, course_group])

            except subprocess.CalledProcessError:
                pass

        return result

    def pre_spawn_start(self, user, spawner):
        """

        :param user:
        :param spawner: Custom spanner of tljh
        :return:
        """
        if self._course_id:
            # Set user working dir
            spawner.user_workingdir = f'/srv/data/courses/{self._course_id}'

        super().pre_spawn_start(user, spawner)

    # def post_spawn_stop(self, user, spawner):
    #     pass
    #     # Todo: Remove sym link of course workspace
