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

    async def authenticate(  # noqa: C901
            self, handler: BaseHandler, data: dict = None
    ) -> dict:
        result = await super().authenticate(handler, data)

        user_roles = handler.get_argument("roles", "Learner").split(",")
        course_id = handler.get_argument("context_id", None)
        course_name = handler.get_argument("context_title", None)
        user_id = handler.get_argument("user_id", None)

        system_username = generate_system_username("jupyter-" + user_id)

        # Ensure user exists. TODO: Move these functions to custom spawner to prevent this
        ensure_user(system_username)

        # Do nothing when course id and user id are not provided
        if course_id and user_id:
            # For instructors replace name with composition of course id and user id
            if any([role in user_roles for role in self._instructor_roles]):
                result["name"] = f"{course_id}-{user_id}"

            # Create course workspace if not existing
            course_dir = f"/srv/data/courses/{course_id}"
            self.log.debug(f"course-dir: {course_dir}")
            if not os.path.exists(course_dir):
                # Owner, group: read, write, execute; other: read, execute
                os.makedirs(course_dir, 0o775)

            # Add symlink of course workspace to home directory
            course_name = course_name if course_name else course_id
            subprocess.check_call(
                ["ln", "-s", course_dir, os.path.expanduser(
                    f"~{system_username}/{course_name}"
                )]
            )
            self.log.debug(["ln", "-s", course_dir, os.path.expanduser(
                    f"~{system_username}/{course_name}"
                )])

            # Add course_name to dict
            result["course_name"] = course_name

            try:
                # Create course linux group with write permissions for course workspace if not existing
                # Unix allows group ids up to 32 chars
                course_group = f"jupyter-c-{course_id}"[:32]
                self.log.debug(f"course-group: {course_group}")
                subprocess.check_call(["groupadd", "-f", course_group])

                # Set group for course workspace
                subprocess.check_call(["chgrp", "-Rf", course_group, course_dir])

                # If instructor add user to course group
                if any([role in user_roles for role in self._instructor_roles]):
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
        super().pre_spawn_start(user, spawner)
        # if user.course_name:
        #     Set user working dir
        #     spawner.user_workingdir = f"{{USERNAME}}/{user.course_name}"

    # def post_spawn_stop(self, user, spawner):
    #     pass
    #     # Todo: Remove sym link of course workspace
