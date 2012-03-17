#:coding=utf-8:

from newauth.backend import ModelAuthBackend

class TestBackend(ModelAuthBackend):
    def authenticate(self, user_id):
        try:
            return self.user_model.objects.get(pk=user_id)
        except self.user_model.DoesNotExist:
            return None

class TestBackend2(ModelAuthBackend):
    def authenticate(self):
        try:
            return self.user_model.objects.get(pk=1)
        except self.user_model.DoesNotExist:
            return None

class TestBackend3(ModelAuthBackend):
    def authenticate(self, user_id):
        try:
            return self.user_model.objects.get(pk=user_id)
        except self.user_model.DoesNotExist:
            return None
