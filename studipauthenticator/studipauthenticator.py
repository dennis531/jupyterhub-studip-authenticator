from jupyterhub.handlers import BaseHandler
from ltiauthenticator import LTIAuthenticator


# class StudipHandler(LTI11AuthenticateHandler):
#     def get(self):
#         self.log.debug("Test-debug")
#
#         self.write("Hello World")


class StudipAuthenticator(LTIAuthenticator):

    username_key = "user_id"

    async def authenticate(  # noqa: C901
        self, handler: BaseHandler, data: dict = None
    ) -> dict:
        user_roles = handler.get_argument("roles", "Learner").split(",")
        course_id = handler.get_argument("context_id", None)
        user_id = handler.get_argument("user_id", None)

        self.log.debug(f"user-id: {handler.request.arguments['user_id']}")

        if course_id and user_id:
            # Set combined user_id of course id and user id if instructor
            if any([role in user_roles for role in ["Instructor", "Administrator", "Staff"]]):
                handler.request.arguments["user_id"] = f"{course_id}-{user_id}".encode()

            self.log.debug(f"user-id: {handler.request.arguments['user_id']}")

        return await super().authenticate(handler, data)
